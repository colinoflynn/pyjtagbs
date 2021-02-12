/******************** (C) COPYRIGHT 2014 STMicroelectronics ********************
* File Name          : version.txt
* Author             : MCD Application Team
* Version            : V1.0.0
* Date               : 05/30/2014
* Description        : Boundary Scan Description Language (BSDL) file for the    
*                      STM32F4xx Microcontrollers
********************************************************************************
* THE PRESENT SOFTWARE WHICH IS FOR GUIDANCE ONLY AIMS AT PROVIDING CUSTOMERS
* WITH CODING INFORMATION REGARDING THEIR PRODUCTS IN ORDER FOR THEM TO SAVE TIME.
* AS A RESULT, STMICROELECTRONICS SHALL NOT BE HELD LIABLE FOR ANY DIRECT,
* INDIRECT OR CONSEQUENTIAL DAMAGES WITH RESPECT TO ANY CLAIMS ARISING FROM THE
* CONTENT OF SUCH SOFTWARE AND/OR THE USE MADE BY CUSTOMERS OF THE CODING
* INFORMATION CONTAINED HEREIN IN CONNECTION WITH THEIR PRODUCTS.
*******************************************************************************/

=======================
How to use BSDL Files :
=======================

The STM32F4xx MCUs integrate two serially connected JTAG TAPs, the boundary scan
TAP (IR is 5-bit wide) and the CortexMx TAP (IR is 4-bit wide).

The package contains :

   + A BSDL File for the CortexMx TAP and is common to all STM32F4xx  devices
   + Boundary scan BSDL Files for each STM32F4xx device on different packages :
      o LQFP64
	  o LQFP100
	  o LQFP144
	  o UFBGA176
	  o LQFP176
	  o WLCSP90

In order to run boundary scan, always provide two BSDL files to your JTAG Boundary scan tool:
the "CortexMx.bsd" and your selected "STM32xx_device_Package.bsd".  

WARNING : Do not combine both BSDL files in a single TAP with 9-bit wide !

For more details on the internal TAPs description refer to the Reference Manual
of the selected STM32xxxx device , Section : JTAG TAP connection.


======================
* V1.0.0 - 05/30/2014
======================
  Created.
  

******************* (C) COPYRIGHT 2014 STMicroelectronics *****END OF FILE
