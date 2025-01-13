#ifndef __SERIALIZER__
#define __SERIALIZER__

#include <stdint.h>

#define HTON(data, buffer, size) serializer::hton((uint8_t*)data, buffer, size); buffer+=size
#define NTOH(data, buffer, size) serializer::hton(buffer, (uint8_t*)data, size); buffer+=size



namespace serializer {

    constexpr bool isBigEndian();

    void hton(uint8_t *data, uint8_t *buffer, int size);

};

struct serializableMessage {
    serializableMessage(const int id) : WORD_ID(id) {}
    virtual int serialize(uint8_t *buffer) = 0;
    virtual int deserialize(uint8_t *buffer) = 0;

    const int WORD_ID;
};

#endif // __SERIALIZER__