/******************************************************************************
 *  Copyright (c) 2016, Xilinx, Inc.
 *  All rights reserved.
 *
 *  Redistribution and use in source and binary forms, with or without
 *  modification, are permitted provided that the following conditions are met:
 *
 *  1.  Redistributions of source code must retain the above copyright notice,
 *     this list of conditions and the following disclaimer.
 *
 *  2.  Redistributions in binary form must reproduce the above copyright
 *      notice, this list of conditions and the following disclaimer in the
 *      documentation and/or other materials provided with the distribution.
 *
 *  3.  Neither the name of the copyright holder nor the names of its
 *      contributors may be used to endorse or promote products derived from
 *      this software without specific prior written permission.
 *
 *  THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
 *  AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO,
 *  THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
 *  PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR
 *  CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
 *  EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
 *  PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS;
 *  OR BUSINESS INTERRUPTION). HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
 *  WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR
 *  OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF
 *  ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
 *
 *****************************************************************************/
/******************************************************************************
 *
 *
 * @file pmod_pwm.c
 *
 * IOP code (MicroBlaze) for Pmod Timer.
 * Pulses can be generated by the Pmod timer.
 * The timer can also detect pulses on the Pmod pin.
 * The input / output pin is assumed to be at Pin 1 of any Pmod.
 * Since the AXI TmrCtr IP's device driver does not support PWM, 
 * the pulses are generated using low-level driver calls.
 * setupTimers() function is used. 
 * pmod_init() function is not called, because IIC and SPI are not used.
 *
 * <pre>
 * MODIFICATION HISTORY:
 *
 * Ver   Who  Date     Changes
 * ----- --- ------- -----------------------------------------------
 * 1.00a pp  05/10/16 release
 * 1.00b yrq 05/27/16 clean up the codes
 * 1.00c yrq 08/08/16 change coding style
 *
 * </pre>
 *
 *****************************************************************************/
#include "xparameters.h"
#include "xtmrctr_l.h"
#include "xgpio.h"
#include "pmod.h"

// Mailbox commands
#define CONFIG_IOP_SWITCH       0x1
#define GENERATE                		0x3
#define STOP                    			0x5

// Added by skb on 6/6/2017
// New mailbox commands to read/write GPIO values
#define READ								0x9
#define WRITE								0x7

/*
 * TIMING_INTERVAL = (TLRx + 2) * AXI_CLOCK_PERIOD
 * PWM_PERIOD = (TLR0 + 2) * AXI_CLOCK_PERIOD
 * PWM_HIGH_TIME = (TLR1 + 2) * AXI_CLOCK_PERIOD
 */

// TCSR0 Timer 0 Control and Status Register
#define TCSR0 0x00
// TLR0 Timer 0 Load Register
#define TLR0 0x04
// TCR0 Timer 0 Counter Register
#define TCR0 0x08
// TCSR1 Timer 1 Control and Status Register
#define TCSR1 0x10
// TLR1 Timer 1 Load Register
#define TLR1 0x14
// TCR1 Timer 1 Counter Register
#define TCR1 0x18
// Default period value for 100000 us
#define MS1_VALUE 99998
// Default period value for 50% duty cycle
#define MS2_VALUE 49998

#define HB3_CHANNEL	1

XGpio hb3_if;

/*
 * Parameters passed in MAILBOX_WRITE_CMD
 * bits 31:16 => period in us
 * bits 15:8 is not used
 * bits 7:1 => duty cycle in %, valid range is 1 to 99
 */

/************************** Function Prototypes ******************************/
void setup_timers(void) {

    // Load timer's Load registers (period, high time)
    XTmrCtr_WriteReg(XPAR_TMRCTR_0_BASEADDR, 0, TLR0, MS1_VALUE);
    XTmrCtr_WriteReg(XPAR_TMRCTR_0_BASEADDR, 1, TLR0, MS2_VALUE);
    /*
     * 0010 1011 0110 =>  no cascade, no all timers, enable pwm, 
     *                    interrupt status, enable timer,
     *                    no interrupt, no load timer, reload, 
     *                    no capture, enable external generate, 
     *                    down counter, generate mode
     */
    XTmrCtr_WriteReg(XPAR_TMRCTR_0_BASEADDR, 0, TCSR0, 0x296);
    XTmrCtr_WriteReg(XPAR_TMRCTR_0_BASEADDR, 1, TCSR0, 0x296);
}

int main(void) {
    int Status;
    u32 cmd;
    u32 Timer1Value, Timer2Value;
    u8 iop_pins[8];
    u32 pwm_pin;
	
	// Added by skb on 6/6/2017
	// Added GPIO channels
	// u32 hb3_inputs;
    u32 gpio_values;
	u32 direction;
	// u32 sensor_a;
	// u32 sensor_b;
    u32 GPIO_data_direction;
    
    /*
     * Configuring Pmod IO switch
     * bit-0 is controlled by the pwm
	 * For the PmodHB3 the outputs are as follows:
	 * bit[0] = Direction (GPIO Output)
	 * bit[1] = Enable (PWM signal)
	 * bit[2] = SA (GPIO Input)
	 * bit[3] = SB (GPIO Input)
     */
    config_pmod_switch(GPIO_0,PWM,GPIO_1,GPIO_2,
                       GPIO_4,GPIO_5,GPIO_6,GPIO_7);
    setup_timers();
	
	// Added by skb on 6/6/2017
	// Add GPIO setup calls, using the XGpio device hb3_if and 
	// setting the direction mask to 0b1100 such that 
	// bits [0:1] are write/output corresponding to the hb3 direction and enable bits
	// bits [2:3] are read/inputs, corresponding to  the hb3 SA and SB sensor inputs
    
    // initialize GPIO driver
    Status = XGpio_Initialize(&hb3_if, XPAR_GPIO_0_DEVICE_ID);
    if (Status != XST_SUCCESS) {
      return XST_FAILURE;
    }
    
    // Set all gpio pins to outputs
	XGpio_SetDataDirection(&hb3_if, HB3_CHANNEL, 0x1);
	
	// initially keep it set to 0's
	XGpio_DiscreteWrite(&hb3_if, HB3_CHANNEL, 0);
	
    while(1){
        while(MAILBOX_CMD_ADDR==0);
        cmd = MAILBOX_CMD_ADDR;
        
        switch(cmd){
            case CONFIG_IOP_SWITCH:
                // read new pin configuration
                pwm_pin = MAILBOX_DATA(0);
                iop_pins[0] = GPIO_0;
                iop_pins[1] = GPIO_1;
                iop_pins[2] = GPIO_2;
                iop_pins[3] = GPIO_3;
                iop_pins[4] = GPIO_4;
                iop_pins[5] = GPIO_5;
                iop_pins[6] = GPIO_6;
                iop_pins[7] = GPIO_7;
				
                // set new pin configuration
                iop_pins[pwm_pin] = PWM;
                config_pmod_switch(iop_pins[0], iop_pins[1], iop_pins[2], 
                                   iop_pins[3], iop_pins[4], iop_pins[5], 
                                   iop_pins[6], iop_pins[7]);
                MAILBOX_CMD_ADDR = 0x0;
                break;
                  
            case GENERATE:
                XTmrCtr_WriteReg(XPAR_TMRCTR_0_BASEADDR, 0, TCSR0, 0x296);
                XTmrCtr_WriteReg(XPAR_TMRCTR_0_BASEADDR, 1, TCSR0, 0x296);
                // period in us
                Timer1Value = MAILBOX_DATA(0) & 0x0ffff;
                XTmrCtr_WriteReg(XPAR_TMRCTR_0_BASEADDR,0,
                                 TLR0,Timer1Value*100);
                // pulse in us
                Timer2Value = (MAILBOX_DATA(1) & 0x07f)*Timer1Value/100;
                XTmrCtr_WriteReg(XPAR_TMRCTR_0_BASEADDR,1,
                                 TLR0,Timer2Value*100);
                MAILBOX_CMD_ADDR = 0x0;
                break;
                
            case STOP:
                // disable timer 0
                XTmrCtr_WriteReg(XPAR_TMRCTR_0_BASEADDR, 0, TCSR0, 0);
                // disable timer 1
                XTmrCtr_WriteReg(XPAR_TMRCTR_0_BASEADDR, 1, TCSR0, 0);
                MAILBOX_CMD_ADDR = 0x0;
                break;
            
			case READ:
				// Read inputs from GPIO_2 and GPIO_3 for the SA and SB values
                GPIO_data_direction =  XGpio_GetDataDirection(&hb3_if, HB3_CHANNEL);
				// hb3_inputs = XGpio_DiscreteRead(&hb3_if, HB3_CHANNEL);
				// sensor_a = (hb3_inputs >> 2) & 0x1;
				// sensor_b = (hb3_inputs >> 3) & 0x1;
				
				// send sensor_a and sensor_b values back
				// This isn't very useful as the sensor values need to be sampled
				// much faster for determining the RPM and direction of the motors
				MAILBOX_DATA(0) = GPIO_data_direction;
                // MAILBOX_DATA(1) = sensor_b;
				MAILBOX_CMD_ADDR = 0x9;
				break;
				
			case WRITE:
				// Write to GPIO_0 for setting the direction
                // xil_printf("Grabbing direction.\n\r");
				 direction = MAILBOX_DATA(0);
                 
                 // xil_printf("Write direction: %d to PMOD HB3\n\r", direction);
                 
				 XGpio_DiscreteWrite(&hb3_if, HB3_CHANNEL, direction);
				 
                 // gpio_values = XGpio_DiscreteRead(&hb3_if, HB3_CHANNEL);
                 
                 // MAILBOX_DATA(0) = gpio_values;
                 
				MAILBOX_CMD_ADDR = 0x0;
				break;
				
            default:
                MAILBOX_CMD_ADDR = 0x0;
                break;
        }
    }
    return 0;
}

