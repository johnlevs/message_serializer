

#ifndef __SERIALIZER__
#define __SERIALIZER__

#include <stdint.h>

#define HTON(data, buffer, size) serializer::hton((uint8_t*)data, buffer, size); buffer+=size
#define NTOH(data, buffer, size) serializer::hton(buffer, (uint8_t*)data, size); buffer+=size



namespace serializer {

    constexpr bool isBigEndian();

    void hton(uint8_t *data, uint8_t *buffer, int size);

};


#endif // __SERIALIZER__