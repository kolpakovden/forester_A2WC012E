// FindCarBerryTipInWriter.java
// @category CarBerry
// Ghidra 12.1.4 Java; read-only report for CarBerry HC16 memory references.
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

public class FindCarBerryTipInWriter extends GhidraScript {
    static final long LO=0x17D6L, HI=0x17DAL;
    static String hx(long x){return Long.toHexString(x);}
    @Override public void run() throws Exception {
        List<String> direct=new ArrayList<>(), refs=new ArrayList<>(), nearby=new ArrayList<>();
        long count=0;
        Listing listing=currentProgram.getListing();
        InstructionIterator it=listing.getInstructions(true);
        while(it.hasNext()){
            monitor.checkCancelled();
            Instruction i=it.next(); count++;
            Function f=currentProgram.getFunctionManager().getFunctionContaining(i.getAddress());
            String name=f==null?"<none>":f.getName();
            String m=i.getMnemonicString();
            for(int k=0;k<i.getNumOperands();k++) for(Object o:i.getOpObjects(k)){
                long n;
                if(o instanceof Scalar)n=((Scalar)o).getUnsignedValue();
                else if(o instanceof Address)n=((Address)o).getOffset();
                else continue;
                if(!(n<=0xffff || (n>=0x20000 && n<=0x2ffff)))continue;
                long a=n&0xffffL;
                String line=i.getAddress()+" | "+name+" | "+i+" | operand="+k+" scalar=0x"+hx(n);
                if(a>=LO&&a<=HI)direct.add(line);
                else if(a>=0x17B0&&a<=0x17FF)nearby.add(line);
            }
            for(Reference r:i.getReferencesFrom()){
                if(r.getToAddress()==null)continue;
                long a=r.getToAddress().getOffset();
                if(a>=LO&&a<=HI)refs.add(i.getAddress()+" | "+name+" | "+r+" | "+i);
            }
        }
        File folder=askDirectory("Choose EXISTING folder for CarBerry report","Save");
        if(folder==null)return;
        if(!folder.isDirectory())throw new IOException("Folder does not exist: "+folder);
        Path out=new File(folder,"carberry_tps_delta_xrefs.txt").toPath();
        try(PrintWriter w=new PrintWriter(Files.newBufferedWriter(out,StandardCharsets.UTF_8))){
            w.println("CarBerry HC16 candidate source report v2 (READ ONLY)");
            w.println("Program: "+currentProgram.getName());
            w.println("Language: "+currentProgram.getLanguageID());
            w.println("Default address space: "+currentProgram.getAddressFactory().getDefaultAddressSpace());
            w.println("Memory blocks:");
            for(MemoryBlock b:currentProgram.getMemory().getBlocks())
                w.println("  "+b.getName()+" "+b.getStart()+".."+b.getEnd()+" initialized="+b.isInitialized()+" execute="+b.isExecute());
            w.println("Functions: "+currentProgram.getFunctionManager().getFunctionCount());
            for(long p:new long[]{0xBA6,0x4E58,0xA7C4}){
                Address a=currentProgram.getAddressFactory().getDefaultAddressSpace().getAddress(p);
                Instruction inst=listing.getInstructionAt(a);
                CodeUnit cu=listing.getCodeUnitAt(a);
                w.println("Probe "+a+" codeUnit="+(cu==null?"none":cu.getClass().getSimpleName())+
                  " instruction="+(inst==null?"NONE":inst));
            }
            w.println("Instructions scanned: "+count);
            w.println("IMPORTANT: missing source references may reside in UNDISASSEMBLED code.");
            w.println("\n=== DIRECT_TARGET ("+direct.size()+") ===");
            for(String s:direct)w.println(s);
            w.println("\n=== REFERENCE_TARGET ("+refs.size()+") ===");
            for(String s:refs)w.println(s);
            w.println("\n=== NEARBY_OPERANDS ("+nearby.size()+") ===");
            for(String s:nearby)w.println(s);
        }
        println("CarBerry v2 report: "+out.toAbsolutePath()+"; instructions="+count);
    }
}
