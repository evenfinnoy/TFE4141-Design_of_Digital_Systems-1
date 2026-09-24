----------------------------------------------------------------------------------
-- Company    :  NTNU
-- Engineer   : Oystein Gjermundnes
--
-- Module Name: mega_adder_controller
-- Description:
--   Control logic for the optimized mega_adder.
----------------------------------------------------------------------------------

library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

entity adder_controller is
  port (
    -- Clocks and resets
    clk             : in  std_logic;
    reset_n         : in  std_logic;

    -- Datapath control signals
    input_reg_en    : out std_logic;
    output_reg_en   : out std_logic;
    output_reg_load : out std_logic;

    -- Control signals for the input interface
    data_in_valid   : in  std_logic;
    data_in_ready   : out std_logic;

    -- Control signal for the 32-bit adder
    add_en          : out std_logic;

    -- Control signals for the output interface
    data_out_valid  : out std_logic;
    data_out_ready  : in  std_logic
  );
end adder_controller;


architecture rtl of adder_controller is

  signal data_in_ready_i        : std_logic;
  signal input_reg_en_i         : std_logic;

  signal data_out_valid_i       : std_logic;
  signal output_reg_shift       : std_logic;

  signal result_ready_r         : std_logic;

  signal input_shift_counter_r  : unsigned(2 downto 0);
  signal output_shift_counter_r : unsigned(1 downto 0);

begin

  --------------------------------------------------------------------------
  -- INPUT HANDSHAKE
  --------------------------------------------------------------------------

  -- Keep the original behavior for now:
  -- inputs are accepted only when the output side is ready.
  data_in_ready_i <= data_out_ready;

  data_in_ready <= data_in_ready_i;

  -- An input word is accepted when both valid and ready are high.
  input_reg_en_i <= data_in_valid and data_in_ready_i;

  input_reg_en <= input_reg_en_i;


  --------------------------------------------------------------------------
  -- ADD ENABLE
  --------------------------------------------------------------------------

  -- Counter values:
  --
  -- 0 -> a0
  -- 1 -> a1
  -- 2 -> a2
  -- 3 -> a3
  -- 4 -> b0
  -- 5 -> b1
  -- 6 -> b2
  -- 7 -> b3
  --
  -- Bit 2 of the 3-bit counter is therefore high for 4..7.
  --
  -- add_en is only asserted when a B word is ACTUALLY accepted.
  add_en <= input_reg_en_i and input_shift_counter_r(2);


  --------------------------------------------------------------------------
  -- INPUT WORD COUNTER
  --------------------------------------------------------------------------

  -- Increment each time a 32-bit input word is accepted.
  process(clk, reset_n)
  begin

    if(reset_n = '0') then

      input_shift_counter_r <= (others => '0');

    elsif(clk'event and clk = '1') then

      if(input_reg_en_i = '1') then
        input_shift_counter_r <= input_shift_counter_r + 1;
      end if;

    end if;

  end process;


  --------------------------------------------------------------------------
  -- OUTPUT WORD COUNTER
  --------------------------------------------------------------------------

  -- Increment each time a 32-bit result word is accepted by the receiver.
  process(clk, reset_n)
  begin

    if(reset_n = '0') then

      output_shift_counter_r <= (others => '0');

    elsif(clk'event and clk = '1') then

      if(output_reg_shift = '1') then
        output_shift_counter_r <= output_shift_counter_r + 1;
      end if;

    end if;

  end process;


  --------------------------------------------------------------------------
  -- RESULT READY
  --------------------------------------------------------------------------

  -- In the old architecture, output_reg_load_r indicated that the 128-bit
  -- addition had completed.
  --
  -- In the new architecture, the result is completed immediately when b3
  -- is accepted, because the four 32-bit additions have already been done.
  process(clk, reset_n)
  begin

    if(reset_n = '0') then

      result_ready_r <= '0';

    elsif(clk'event and clk = '1') then

      -- Counter = 7 means the current accepted input is b3.
      -- On this same edge, the datapath stores y3 and y_r becomes complete.
      if(input_reg_en_i = '1' and input_shift_counter_r = 7) then

        result_ready_r <= '1';

      -- Clear the initial "result ready" flag after an output word
      -- has actually been transferred.
      elsif(output_reg_shift = '1') then

        result_ready_r <= '0';

      end if;

    end if;

  end process;


  --------------------------------------------------------------------------
  -- OUTPUT VALID GENERATION
  --------------------------------------------------------------------------

  -- Data is valid while:
  --
  -- 1. A fresh result has just become ready
  -- OR
  -- 2. We are in the middle of shifting out the four result words.
  process(output_shift_counter_r, result_ready_r)
  begin

    if(output_shift_counter_r /= "00" or result_ready_r = '1') then

      data_out_valid_i <= '1';

    else

      data_out_valid_i <= '0';

    end if;

  end process;


  --------------------------------------------------------------------------
  -- OUTPUT HANDSHAKE / DATAPATH CONTROL
  --------------------------------------------------------------------------

  data_out_valid <= data_out_valid_i;

  -- An output word is transferred when valid and ready are both high.
  output_reg_shift <= data_out_valid_i and data_out_ready;

  -- Shift y_r only after an output word has actually been transferred.
  output_reg_en <= output_reg_shift;


  --------------------------------------------------------------------------
  -- UNUSED LEGACY SIGNAL
  --------------------------------------------------------------------------

  -- The optimized datapath no longer needs a separate "load output register"
  -- control signal because y_r is built incrementally during b0-b3.
  --
  -- Keep the port temporarily so the old top-level can still compile.
  output_reg_load <= '0';


end rtl;