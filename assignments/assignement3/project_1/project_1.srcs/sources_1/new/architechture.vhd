----------------------------------------------------------------------------------
-- Company: 
-- Engineer: 
-- 
-- Create Date: 09/01/2026 02:13:20 PM
-- Design Name: 
-- Module Name: architechture - Behavioral
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

entity latch is
    Port(S,R: in std_ulogic; 
    Q: out std_ulogic);
end latch;

architecture behavioral of latch is
begin
    process (S, R)
    begin
        if R = '1' then
            Q <= '0';
        elsif S = '1' then
            Q <= '1';
        end if;
    end process;
end behavioral;