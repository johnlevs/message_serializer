// MIT License

// Copyright(c) 2024 johnlevs

// Permission is hereby granted, free of charge, to any person obtaining a copy
// of this software and associated documentation files(the "Software"), to deal
// in the Software without restriction, including without limitation the rights
// to use, copy, modify, merge, publish, distribute, sublicense, and /or sell
// copies of the Software, and to permit persons to whom the Software is
// furnished to do so, subject to the following conditions :

// The above copyright notice and this permission notice shall be included in all
// copies or substantial portions of the Software.

// THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
// IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
// FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.IN NO EVENT SHALL THE
// AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
// LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
// OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
// SOFTWARE.


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
