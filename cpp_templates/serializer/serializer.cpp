

#include "serializer.h"

#include <string.h>


constexpr bool serializer::isBigEndian()
{
    constexpr uint32_t i = 1;
    return ((uint8_t *)&i)[0] == 0;
}

void serializer::hton(uint8_t *data, uint8_t *buffer, int size)
{
    if (isBigEndian()) {
        memcpy(buffer, data, size);
        return;
    }


    switch (size) {
    case (sizeof(uint8_t)):
        *buffer = *data;
        break;
    case (sizeof(uint16_t)):
        *(uint16_t *)buffer = __builtin_bswap16(*(uint16_t *)data);
        break;
    case (sizeof(uint32_t)):
        *(uint32_t *)buffer = __builtin_bswap32(*(uint32_t *)data);
        break;
    case (sizeof(uint64_t)):
        *(uint64_t *)buffer = __builtin_bswap64(*(uint64_t *)data);
        break;
    default:
        for (int i = 0; i < size; i++)
            buffer[i] = data[size - i - 1];
        break;
    }
}
