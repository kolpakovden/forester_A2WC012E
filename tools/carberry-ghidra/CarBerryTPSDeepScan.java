// CarBerryTPSDeepScan.java
// @category CarBerry
// Ghidra 12.1.4 Java: read-only ROM raw byte scan + listing indexed-write inventory.
// Never treats raw byte pairs as proof of decoded instructions.
import ghidra.app.script.GhidraScript;
import ghidra.program.model.listing.*;
import ghidra.program.model.address.*;
import ghidra.program.model.mem.*;
import ghidra.program.model.scalar.*;
import ghidra.program.model.symbol.*;
import java.io.*;
import java.nio.file.*;
import java.nio.charset.StandardCharsets;
import java.util.*;

public class CarBerryTPSDeepScan extends GhidraScript {
    final List<String> direct=new ArrayList<>(), near=new ArrayList<>(), ptr=new ArrayList<>();
    final List<String> raw=new ArrayList<>(), gaps=new ArrayList<>(), indexed=new ArrayList<>();
    final Map<String,Integer> counts=new HashMap<>();
    static final int LO=0x17D6,HI=0x17DA;
    String fn(Address a){Function f=currentProgram.getFunctionManager().getFunctionContaining(a);return f==null?"<unassigned>":f.getName();}
    String csv(String s){return "\""+s.replace("\"","\"\"")+"\"";}
    boolean writer(String s){return s.startsWith("ST")||s.startsWith("CLR")||s.startsWith("INC")||s.startsWith("DEC")||s.startsWith("BSET")||s.startsWith("BCLR")||s.startsWith("MOV")||s.startsWith("NEG")||s.startsWith("COM")||s.startsWith("ASL")||s.startsWith("ASR")||s.startsWith("ROL")||s.startsWith("ROR");}
    void inspect(Instruction i){
        String m=i.getMnemonicString().toUpperCase(), t=i.toString(), f=fn(i.getAddress());
        String desc=i.getAddress()+" | "+f+" | "+t;
        boolean write=writer(m);
        for(int k=0;k<i.getNumOperands();k++)for(Object o:i.getOpObjects(k)){
            long n;
            if(o instanceof Scalar)n=((Scalar)o).getUnsignedValue();
            else if(o instanceof Address)n=((Address)o).getOffset();
            else continue;
            if(!(n<=0xffff || (n>=0x20000 && n<=0x2ffff)))continue;
            long a=n&0xffffL;
            if(a>=LO&&a<=HI)direct.add((write?"POSSIBLE_WRITE":"READ/OTHER")+" | "+desc+" | scalar=0x"+Long.toHexString(n));
            if(a>=0x17B0&&a<=0x17FF&&write)near.add(desc+" | nearby scalar=0x"+Long.toHexString(n));
            if(a>=0x17A0&&a<=0x1800&&(m.startsWith("LDX")||m.startsWith("LDY")||m.startsWith("LDE")||m.startsWith("LEA"))&&t.contains("#"))
                ptr.add(desc+" | pointer candidate 0x"+Long.toHexString(n));
        }
        for(Reference r:i.getReferencesFrom()){
            if(r.getToAddress()==null)continue;
            long n=r.getToAddress().getOffset();
            if(n>=LO&&n<=HI)direct.add("REF "+r.getReferenceType()+" -> "+r.getToAddress()+" | "+desc);
        }
        if(write&&(t.contains(",IX")||t.contains(",IY")||t.contains(",IZ"))){
            indexed.add(csv(i.getAddress().toString())+","+csv(f)+","+csv(m)+","+csv(t));
            counts.put(f,counts.getOrDefault(f,0)+1);
        }
    }
    void rawScan(MemoryBlock b)throws Exception{
        if(!b.isInitialized()||!b.isExecute())return;
        long len=b.getSize();
        if(len>2000000L){raw.add("SKIP large block "+b.getName());return;}
        byte[] bytes=new byte[(int)len];currentProgram.getMemory().getBytes(b.getStart(),bytes);
        int hits=0;
        for(int j=0;j+1<bytes.length;j++){
            if((bytes[j]&255)!=0x17 || (bytes[j+1]&255)<0xD6 || (bytes[j+1]&255)>0xDA)continue;
            Address a=b.getStart().add(j);
            Instruction i=currentProgram.getListing().getInstructionContaining(a);
            String context=i==null?"UNDEFINED_OR_DATA":"IN_CODE "+i.getAddress()+" "+fn(i.getAddress());
            raw.add(a+" | 17 "+String.format("%02X",bytes[j+1]&255)+" | "+context+
             " | before="+String.format("%02X %02X",j>=2?bytes[j-2]&255:0,j>=1?bytes[j-1]&255:0));
            hits++;
        }
        raw.add("TOTAL "+b.getName()+" = "+hits);
        boolean[] covered=new boolean[bytes.length];
        InstructionIterator it=currentProgram.getListing().getInstructions(b.getStart(),true);
        while(it.hasNext()){
            Instruction i=it.next();if(i.getAddress().compareTo(b.getEnd())>0)break;
            long off=i.getAddress().subtract(b.getStart());
            for(int j=0;j<i.getLength();j++)if(off+j>=0&&off+j<len)covered[(int)(off+j)]=true;
        }
        for(int j=0;j<covered.length;){
            if(covered[j]){j++;continue;}
            int st=j;while(j<covered.length&&!covered[j])j++;
            if(j-st>=16)gaps.add(b.getStart().add(st)+" .. "+b.getStart().add(j-1)+" | "+(j-st)+" bytes");
        }
    }
    void section(PrintWriter w,String title,List<String> vals,int cap){
        w.println("\n=== "+title+" ("+vals.size()+") ===");
        for(int j=0;j<Math.min(cap,vals.size());j++)w.println(vals.get(j));
        if(vals.size()>cap)w.println("TRUNCATED: "+(vals.size()-cap)+" other entries");
    }
    @Override public void run()throws Exception{
        long n=0;InstructionIterator it=currentProgram.getListing().getInstructions(true);
        while(it.hasNext()){monitor.checkCancelled();inspect(it.next());n++;}
        for(MemoryBlock b:currentProgram.getMemory().getBlocks()){monitor.checkCancelled();rawScan(b);}
        File dir=askDirectory("Choose EXISTING folder for CarBerry deep scan","Save");
        if(dir==null)return;
        if(!dir.isDirectory())throw new IOException("Folder not found: "+dir);
        Path report=new File(dir,"carberry_tps_delta_deep.txt").toPath();
        Path csvfile=new File(dir,"carberry_indexed_writes.csv").toPath();
        try(PrintWriter w=new PrintWriter(Files.newBufferedWriter(report,StandardCharsets.UTF_8))){
            w.println("CarBerry HC16 TPS delta deeper scan v3 (READ ONLY)");
            w.println("Program: "+currentProgram.getName());
            w.println("Processor: "+currentProgram.getLanguageID());
            w.println("Instructions: "+n+"; functions: "+currentProgram.getFunctionManager().getFunctionCount());
            w.println("CAUTION: raw byte pairs, indexed stores, and address-space aliases require manual confirmation.");
            section(w,"DIRECT_TARGET and REFERENCES",direct,300);
            section(w,"POSSIBLE_POINTER_BASES",ptr,300);
            section(w,"NEARBY_RAM_WRITES",near,300);
            section(w,"RAW_ROM_PAIR_17D6_TO_17DA",raw,400);
            w.println("\n=== INDEXED_WRITE_TOTAL ("+indexed.size()+") ===");
            List<Map.Entry<String,Integer>> sorted=new ArrayList<>(counts.entrySet());
            sorted.sort((a,b)->Integer.compare(b.getValue(),a.getValue()));
            for(int j=0;j<Math.min(100,sorted.size());j++)w.println(sorted.get(j).getKey()+" | "+sorted.get(j).getValue());
            section(w,"LONG_NON_INSTRUCTION_REGIONS",gaps,160);
        }
        try(PrintWriter w=new PrintWriter(Files.newBufferedWriter(csvfile,StandardCharsets.UTF_8))){
            w.println("address,function,mnemonic,instruction");
            for(String s:indexed)w.println(s);
        }
        println("CarBerry deep scan report: "+report.toAbsolutePath());
        println("CarBerry indexed writes: "+csvfile.toAbsolutePath());
        println("Instructions scanned="+n+" indexed-write candidates="+indexed.size());
    }
}
