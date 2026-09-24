----------------------------------------------------------------------------------
-- Company    : NTNU
-- Engineer   : Oystein Gjermundnes
--
-- Module Name: mega_adder
-- Description:
--   The mega adder adds two 128-bit numbers and produces a 128-bit sum.
--   Inputs are shifted in 32 bits at a time and the result is shifted
--   out 32 bits at a time.
----------------------------------------------------------------------------------

library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

entity mega_adder is
  port (
    -- Clocks and resets
    clk            : in  std_logic;
    reset_n        : in  std_logic;

    -- Data input interface
    data_in_valid  : in  std_logic;
    data_in_ready  : out std_logic;
    data_in        : in  std_logic_vector(31 downto 0);

    -- Data output interface
    data_out_valid : out std_logic;
    data_out_ready : in  std_logic;
    data_out       : out std_logic_vector(31 downto 0)
  );
end mega_adder;


architecture rtl of mega_adder is

  --------------------------------------------------------------------------
  -- Internal control signals
  --------------------------------------------------------------------------

  signal input_reg_en  : std_logic;
  signal output_reg_en : std_logic;
  signal add_en        : std_logic;

begin


  --------------------------------------------------------------------------
  -- DATAPATH
  --------------------------------------------------------------------------

  u_adder_datapath : entity work.adder_datapath
    port map (

      -- Clocks and resets
      clk           => clk,
      reset_n       => reset_n,

      -- Data input
      data_in       => data_in,
      input_reg_en  => input_reg_en,

      -- 32-bit addition control
      add_en        => add_en,

      -- Data output
      data_out      => data_out,
      output_reg_en => output_reg_en

    );


  --------------------------------------------------------------------------
  -- CONTROLLER
  --------------------------------------------------------------------------

  u_adder_controller : entity work.adder_controller
    port map (

      -- Clocks and resets
      clk             => clk,
      reset_n         => reset_n,

      -- Datapath controls
      input_reg_en    => input_reg_en,
      output_reg_en   => output_reg_en,

      -- Legacy controller output.
      -- No longer needed by the optimized datapath.
      output_reg_load => open,

      -- Input interface
      data_in_valid   => data_in_valid,
      data_in_ready   => data_in_ready,

      -- Addition control
      add_en           => add_en,

      -- Output interface
      data_out_valid  => data_out_valid,
      data_out_ready  => data_out_ready

    );


end rtl;