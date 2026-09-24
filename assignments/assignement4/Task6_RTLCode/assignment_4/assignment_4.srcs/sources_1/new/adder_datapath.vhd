----------------------------------------------------------------------------------
-- Company    :  NTNU
-- Engineer   : �ystein Gjermundnes
-- 
-- Module Name: mega_adder_datapath
-- Description:   
--   Datapath for the mega_adder. The datapath consists of shift registers
--   at the inputs and outputs and a large 128 bit adder.
--
--   CHALLENGE 1:
--   Set different synthesis constraints for the max frequency and check how the
--   area of the design changes.
--  
--   CHALLENGE 2: 
--   Can you think of a way to significantly increase the max clock frequency 
--   as well as reducing the area?
----------------------------------------------------------------------------------
library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

entity adder_datapath is
  port (      
    -- Clocks and resets
    clk             : in std_logic;
    reset_n         : in std_logic;
    
    -- Data in interface       
    data_in         : in std_logic_vector (31 downto 0);
    input_reg_en    : in std_logic;
    
    -- Computation interfac
    add_en          : in std_logic;
    
    -- Data out interface
    data_out        : out std_logic_vector (31 downto 0);
    output_reg_en   : in std_logic);
end adder_datapath;

architecture rtl of adder_datapath is

  -- Signals associated with the input registers
  signal a_r: std_logic_vector(127 downto 0);
  
  -- Signals associated with the output registers
  signal y_r, y_nxt: std_logic_vector(127 downto 0);
  
  -- Signals associated with carry
  signal carry_r, carry_nxt : unsigned(0 downto 0);
    
begin

  -- ***************************************************************************
  -- Register a_r
  -- ***************************************************************************
  process (clk, reset_n) begin
    if(reset_n = '0') then
        a_r <= (others => '0');
    elsif(clk'event and clk='1') then
        if(input_reg_en = '1') then
            if(add_en = '0') then
                a_r <= data_in & a_r(127 downto 32);
            else
                a_r <= x"00000000" & a_r(127 downto 32);
            end if;
        end if;
     end if;
   end process;

  -- ***************************************************************************
  -- Register y_r
  -- Add the content of a and b and store it in y.
  -- Logic for shifting out the content of y_r to data_out
  -- ***************************************************************************
  process (clk, reset_n) begin
    if(reset_n = '0') then
      y_r <= (others => '0');  
      carry_r <= (others => '0');   
    elsif(clk'event and clk='1') then
        if(add_en = '1') then
            y_r     <= y_nxt;
            carry_r <= carry_nxt;
        elsif(input_reg_en = '1') then
            carry_r <= (others => '0');
        elsif(output_reg_en = '1') then
            y_r <= y_nxt;
        end if;
    end if;
  end process;
  
  process (y_r, a_r, data_in, add_en, carry_r) 
    variable sum_ext : unsigned(32 downto 0);
  begin
    if(add_en = '1') then
      sum_ext := ('0' & unsigned(a_r(31 downto 0))) + 
                ('0' & unsigned(data_in)) + resize(carry_r, 33);
      carry_nxt <= sum_ext(32 downto 32);
      y_nxt <= std_logic_vector(sum_ext(31 downto 0)) & y_r(127 downto 32);
    else
       y_nxt <= x"00000000" & y_r(127 downto 32);
       carry_nxt <= carry_r;
    end if;
  end process;
  
  data_out <= y_r(31 downto 0);

end rtl;
