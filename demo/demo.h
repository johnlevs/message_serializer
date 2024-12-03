// =========================================================================
// THIS CODE HAS BEEN AUTOMATICALLY GENERATED USING 'message_serializer' TOOL
//       https://github.com/johnlevs/message_serializer
//       Generated on: //2024-12-02 20:58:39// 
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

#ifndef _DEMO_H_
#define _DEMO_H_

#include "serializer/serializer.h"

#include <stdint.h>

namespace DEMO {
	enum class wordIDs {
		LIGHTBULB__lightBulbStatusWord,
		LED__ledStatusWord,

		WORDID_COUNT,
		INVALID_WORDID = 0xFFFF
	};

	namespace LIGHTBULB {
		/**
		* @brief I contain the status of a light bulb
		* @param brightness The brightness of the light bulb
		* @param colorR The color of the light bulb
		* @param colorG The color of the light bulb
		* @param colorB The color of the light bulb
		* @param powerOn The power state of the light bulb
		* @param powerOff The power state of the light bulb
		* @param broken True (1) if the light bulb is broken
		*/
		struct lightBulbStatusWord : public serializableMessage {
			/******************************************** USER DATA ********************************************/

			uint8_t brightness = 5;	// he brightness of the light bul
			uint8_t colorR;	// he color of the light bul
			uint8_t colorG;	// he color of the light bul
			uint8_t colorB;	// he color of the light bul
			uint8_t powerOn;	// he power state of the light bul
			uint8_t powerOff;	// he power state of the light bul
			uint8_t broken;	// rue (1) if the light bulb is broke
			/******************************************** SERIALIZATION ********************************************/

			static constexpr uint16_t SIZE = sizeof(brightness) + sizeof(colorR) + sizeof(colorG) + sizeof(colorB) + sizeof(powerOn) + sizeof(powerOff) + sizeof(broken) + 0;
			static constexpr wordIDs WORDID = wordIDs::LIGHTBULB__lightBulbStatusWord;
			int serialize(uint8_t *buffer) override;
			int deserialize(uint8_t *buffer) override;
		};

		constexpr uint8_t LIGHTBULB_COUNT = 2;

	}; // namespace LIGHTBULB

	namespace LED {
		constexpr uint8_t LED_COUNT = LIGHTBULB::LIGHTBULB_COUNT;

		enum states {
			ON,
			OFF,
		}; // enum states


		/**
		* @brief I contain the status of a 20 led light strip
		* @param lightStatuses The status of each light bulb in the strip
		* @param connectedToInternet True (1) if the light bulb is connected to the internet
		* @param test 
		*/
		struct ledStatusWord : public serializableMessage {
			/******************************************** USER DATA ********************************************/

			LIGHTBULB::lightBulbStatusWord lightStatuses[LED::LED_COUNT];	// he status of each light bulb in the stri
			uint8_t connectedToInternet;	// rue (1) if the light bulb is connected to the interne
			uint8_t test = LED::states::OFF;
			/******************************************** SERIALIZATION ********************************************/

			static constexpr uint16_t SIZE = LIGHTBULB::lightBulbStatusWord::SIZE  * LED::LED_COUNT + sizeof(connectedToInternet) + sizeof(test) + 0;
			static constexpr wordIDs WORDID = wordIDs::LED__ledStatusWord;
			int serialize(uint8_t *buffer) override;
			int deserialize(uint8_t *buffer) override;
		};

	}; // namespace LED

	constexpr uint16_t __max_message_size()
	{
		uint16_t max = 0;
		max = (LIGHTBULB::lightBulbStatusWord::SIZE > max) ? LIGHTBULB::lightBulbStatusWord::SIZE : max;
		max = (LED::ledStatusWord::SIZE > max) ? LED::ledStatusWord::SIZE : max;
		return max;
	}

	constexpr uint16_t MAX_MESSAGE_SIZE = __max_message_size();

} // namespace DEMO

#endif	//_DEMO_H_

