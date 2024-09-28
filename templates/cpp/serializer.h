


#ifndef __SERIALIZER__
#define __SERIALIZER__

#include <stdint.h>

typedef uint8_t u8;
typedef uint16_t u16;
typedef uint32_t u32;
typedef uint64_t u64;
typedef int8_t i8;
typedef int16_t i16;
typedef int32_t i32;
typedef int64_t i64;
typedef float f32;
typedef double f64;

#define HTON(data, buffer, size) serializer::hton((u8*)data, buffer, size); buffer+=size
#define NTOH(data, buffer, size) serializer::hton(buffer, (u8*)data, size); buffer+=size



namespace serializer {

    constexpr bool isBigEndian();

    void hton(u8 *data, u8 *buffer, int size);

};

struct serializableMessage {
    virtual int serialize(u8 *buffer) = 0;
    virtual int deserialize(u8 *buffer) = 0;
};

#endif // __SERIALIZER__