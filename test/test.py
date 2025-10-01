import cocotb
from cocotb.clock import Clock
from cocotb.triggers import ClockCycles, RisingEdge, FallingEdge, Timer

@cocotb.test()
async def test_binary_counter(dut):
    dut._log.info("Starting Counter Test")

    # Set the clock to 100 KHz (as defined in info.yaml)
    cocotb.start_soon(Clock(dut.clk, 10, unit="us").start())

    # initial inputs
    dut.ena.value = 1
    dut.rst_n.value = 1
    dut.ui_in.value = 0b100 # output_en = 0, count_en = 0, load_en = 0 (in said order)
    dut.uio_in.value = 0
    await ClockCycles(dut.clk, 2) # settle inputs


    dut._log.info("Testing Basic Counting")
    dut.ui_in.value = 0b110         # output_en=1, count_en=1, load_en=0
    await ClockCycles(dut.clk, 1)   # settle inputs
    for i in range(1, 5):
        await ClockCycles(dut.clk, 1) # wait for output to update
        assert int(dut.uo_out.value) == i, f"Count cycle {i}: expected {i}, got {int(dut.uo_out.value)}"


    dut._log.info("Testing Asynchronous Reset")
    dut.rst_n.value = 0             
    await ClockCycles(dut.clk, 2)   # wait for reset to complete (input and update output)
    assert int(dut.uo_out.value) == 0, f"Expected 0 after reset, got {int(dut.uo_out.value)}"
    dut.rst_n.value = 1             
    await ClockCycles(dut.clk, 2)   # wait for released reset to complete (input and update output)
    assert int(dut.uo_out.value) == 1, f"Expected 1 after reset and clock cycle, got {int(dut.uo_out.value)}"


    dut._log.info("Testing Synchronous Load")
    load_value = 0x42
    dut.uio_in.value = load_value
    dut.ui_in.value = 0b101  # output_en=1, count_en=0, load_en=1
    await ClockCycles(dut.clk, 2)  # load happens (input and update output)
    assert int(dut.uo_out.value) == load_value, f"Load test: expected {load_value}, got {int(dut.uo_out.value)}"
    

    dut._log.info("Testing Counting from loaded value")
    dut.ui_in.value = 0b110 # output_en=1, count_en=1, load_en=0
    await ClockCycles(dut.clk, 1) # settle inputs
    for i in range(1, 4):
        await ClockCycles(dut.clk, 1)
        assert int(dut.uo_out.value) == (load_value + i), f"Count from load {i}: expected {(load_value + i)}, got {int(dut.uo_out.value)}"
    

    dut._log.info("Testing Disable Count")
    dut.ui_in.value = 0b100  # output_en=1, count_en=0, load_en=0
    await ClockCycles(dut.clk, 1)  # settle input
    current_count = int(dut.uo_out.value) 
    await ClockCycles(dut.clk, 20)
    assert int(dut.uo_out.value) == current_count, f"Count disable: expected {current_count}, got {int(dut.uo_out.value)}"
    

    dut._log.info("Testing 8-bit Overflow")
    dut.uio_in.value = 0xFF
    dut.ui_in.value = 0b101 # output_en=1, count_en=0, load_en=1
    await ClockCycles(dut.clk, 2) # load happens (input and update output)
    assert int(dut.uo_out.value) == 0xFF, "Failed to load 0xFF"
    dut.ui_in.value = 0b110 # output_en=1, count_en=1, load_en=0
    await ClockCycles(dut.clk, 2) # count happens (input and update output)
    assert int(dut.uo_out.value) == 0, f"Overflow test: expected 0, got {int(dut.uo_out.value)}"
    
    dut._log.info("All tests passed!")