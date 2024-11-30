// =========================================================================
// THIS CODE HAS BEEN AUTOMATICALLY GENERATED USING 'message_serializer' TOOL
//       https://github.com/johnlevs/message_serializer
//       Generated on: //2024-11-29 21:33:16// 
// =========================================================================
// MIT License
// 
// Copyright (c) 2024 johnlevs
// 
// Permission is hereby granted, free of charge, to any person obtaining a copy
// of this software and associated documentation files (the "Software"), to deal
// in the Software without restriction, including without limitation the rights
// to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
// copies of the Software, and to permit persons to whom the Software is
// furnished to do so, subject to the following conditions:
// 
// The above copyright notice and this permission notice shall be included in all
// copies or substantial portions of the Software.
// 
// THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
// IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
// FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
// AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
// LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
// OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
// SOFTWARE.

#include "demo.h"

int DEMO::LIGHTBULB::lightBulbStatusWord::serialize(uint8_t *buffer) 
{
	uint8_t* itr = buffer;
	HTON(&brightness, itr, sizeof(brightness));
	HTON(&colorR, itr, sizeof(colorR));
	HTON(&colorG, itr, sizeof(colorG));
	HTON(&colorB, itr, sizeof(colorB));
	HTON(&powerOn, itr, sizeof(powerOn));
	HTON(&powerOff, itr, sizeof(powerOff));
	HTON(&broken, itr, sizeof(broken));
	return itr - buffer;
}


int DEMO::LIGHTBULB::lightBulbStatusWord::deserialize(uint8_t *buffer) 
{
	uint8_t* itr = buffer;
	NTOH(&brightness, itr, sizeof(brightness));
	NTOH(&colorR, itr, sizeof(colorR));
	NTOH(&colorG, itr, sizeof(colorG));
	NTOH(&colorB, itr, sizeof(colorB));
	NTOH(&powerOn, itr, sizeof(powerOn));
	NTOH(&powerOff, itr, sizeof(powerOff));
	NTOH(&broken, itr, sizeof(broken));
	return itr - buffer;
}


int DEMO::LED::ledStatusWord::serialize(uint8_t *buffer) 
{
	uint8_t* itr = buffer;
	for(int i = 0; i < LED_COUNT; i++) {
		itr += lightStatuses[i].serialize(itr);
	}
	HTON(&connectedToInternet, itr, sizeof(connectedToInternet));
	HTON(&test, itr, sizeof(test));
	return itr - buffer;
}


int DEMO::LED::ledStatusWord::deserialize(uint8_t *buffer) 
{
	uint8_t* itr = buffer;
	for(int i = 0; i < LED_COUNT; i++) {
		itr += lightStatuses[i].deserialize(itr);
	}
	NTOH(&connectedToInternet, itr, sizeof(connectedToInternet));
	NTOH(&test, itr, sizeof(test));
	return itr - buffer;
}


