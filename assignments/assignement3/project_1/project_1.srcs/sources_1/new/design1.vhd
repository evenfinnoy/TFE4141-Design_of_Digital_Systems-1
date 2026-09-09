----------------------------------------------------------------------------------
-- Company: 
-- Engineer: 
-- 
-- Create Date: 09/08/2026 04:36:56 PM
-- Design Name: 
-- Module Name: design1 - Behavioral
-- Project Name: 
-- Target Devices: 
-- Tool Versions: 
-- Description: 
-- 
-- Dependencies: 
-- 
-- Revision:
-- Revision 0.01 - File Created
-- Additional Comments:
-- 
----------------------------------------------------------------------------------


library IEEE;
use IEEE.STD_LOGIC_1164.ALL;

-- Uncomment the following library declaration if using
-- arithmetic functions with Signed or Unsigned values
--use IEEE.NUMERIC_STD.ALL;

-- Uncomment the following library declaration if instantiating
-- any Xilinx leaf cells in this code.
--library UNISIM;
--use UNISIM.VComponents.all;

entity assignment3 is
    port (clk: in  std_ulogic;
        reset: in  std_ulogic;
        a, b: in  std_ulogic;
        y: out std_ulogic);
end entity assignment3;

architecture design2 of assignment3 is
begin
    process(clk, reset) is
        variable t : std_ulogic;
    begin
        if reset = '1' then
            t := '0';
            y <= '0';
        elsif rising_edge(clk) then
            t := a xor b;
            y <= t;
        end if;
    end process;
end architecture design2;
