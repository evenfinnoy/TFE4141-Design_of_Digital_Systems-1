library IEEE;
use IEEE.STD_LOGIC_1164.ALL;

entity test_bench is 
end entity test_bench;

architecture test_latch of test_bench is
    signal A, B, Q, QN: std_ulogic;
    begin
        DUT: entity work.latch(behavioral)
        port map (A => A, B => B, Q => Q, QN => QN);
    stimulus: process is
        begin
            A <= '1' ; B <= '0' ;
            wait for 10 ns ;
            A <= '0' ;
            wait for 10 ns ;
            B <= '1' ;
            wait for 10 ns ;
            B <= '0' ;
            wait for 10 ns ;
            B <= '1' ; A <= '1' ;
            wait; --suspends the process so it does not loop :)
        end process stimulus; 
end architecture test_latch;