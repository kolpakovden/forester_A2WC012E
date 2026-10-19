/* Offline-only CarBerry arithmetic research; not an SH7055 hook.
 * Model parity is NOT HC16 opcode validation. */
#include <stdint.h>
uint16_t tipin_base_q8_8(const uint8_t axis[18], const uint8_t values[18], uint8_t x) {
    if (x <= axis[0]) return (uint16_t)values[0] << 8;
    if (x >= axis[17]) return (uint16_t)values[17] << 8;
    for (unsigned i=0;i<17;++i) if(x<axis[i+1]) {
        uint32_t fraction=((uint32_t)(x-axis[i])<<16)/(axis[i+1]-axis[i]);
        if(values[i+1]<values[i]) return 0;
        uint32_t inc=((uint32_t)(values[i+1]-values[i])*256u*fraction)>>16;
        return (uint16_t)(((uint16_t)values[i]<<8)+inc);
    }
    return (uint16_t)values[17]<<8;
}
uint32_t tipin_compensated_raw(uint16_t base_q8_8,uint8_t rpm,uint8_t boost_error,uint8_t ect) {
    uint32_t product=(uint32_t)rpm*boost_error*ect;
    uint32_t factor=product>>4;
    if(factor>65535u)factor=65535u;
    return ((uint32_t)base_q8_8*factor)>>16;
}
uint8_t tipin_uniform8(const uint8_t *nodes,uint8_t size,uint8_t raw,uint8_t scale,uint8_t start) {
    uint32_t prod=(raw<start)?0:((uint32_t)(raw-start)*scale<<8);
    unsigned idx=prod>>16;
    if(idx>=(unsigned)(size-1))return nodes[size-1];
    uint16_t frac=(uint16_t)prod;
    if(nodes[idx+1]>=nodes[idx])return (uint8_t)(nodes[idx]+(((uint32_t)(nodes[idx+1]-nodes[idx])*frac)>>16));
    return (uint8_t)(nodes[idx]-((((uint32_t)(nodes[idx]-nodes[idx+1])*frac)+65535u)>>16));
}
uint8_t tipin_uniform16(const uint8_t *nodes,uint8_t size,uint16_t raw,uint16_t scale,uint16_t start) {
    uint32_t prod=(raw<start)?0:(uint32_t)(raw-start)*scale;
    unsigned idx=prod>>16;
    if(idx>=(unsigned)(size-1))return nodes[size-1];
    uint16_t frac=(uint16_t)prod;
    if(nodes[idx+1]>=nodes[idx])return (uint8_t)(nodes[idx]+(((uint32_t)(nodes[idx+1]-nodes[idx])*frac)>>16));
    return (uint8_t)(nodes[idx]-((((uint32_t)(nodes[idx]-nodes[idx+1])*frac)+65535u)>>16));
}
