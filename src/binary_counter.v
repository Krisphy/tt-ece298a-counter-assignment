// Krish Patel
// ECE 298a - September 30, 2025
// 8-bit Programmable Binary Counter With Asynchronous Reset, Synchronous Load and Tri-state Outputs

`default_nettype none

module tt_um_krisphy_binary_counter (
    input  wire [7:0] ui_in,    // Dedicated inputs
    output wire [7:0] uo_out,   // Dedicated outputs
    input  wire [7:0] uio_in,   // IOs: Input path
    output wire [7:0] uio_out,  // IOs: Output path
    output wire [7:0] uio_oe,   // IOs: Enable path (active high: 0=input, 1=output)
    input  wire       ena,      // always 1 when the design is powered, so you can ignore it
    input  wire       clk,      // clock
    input  wire       rst_n     // reset_n - low to reset
);

    // Input signal assignments
    wire load_en = ui_in[0];            // Load enable signal (synchronous load)
    wire count_en = ui_in[1];           // Count enable (synchronous)
    wire output_en = ui_in[2];          // Output enable (for tri-state, asynchronous)
    wire [7:0] load_data = uio_in;      // 8-bit load data (synchronous load)

    // Internal counter register
    reg [7:0] count = 8'b0;
    
    // Tri-state output
    assign uo_out = output_en ? count : 8'bz;

    // Counter logic with asynchronous reset and synchronous load
    always @(posedge clk or negedge rst_n) begin
        if (rst_n == 0) begin
            count <= 8'b0;  // Asynchronous reset, happens before any other logic
        end else begin
            if (load_en) begin // Higher priority than counting up
                count <= load_data;  // Synchronous load, only hits on a clock edge as reset triggers happen earlier
            end else if (count_en) begin
                count <= count + 1'b1;  // Count up when enabled, overflows at (255 + 1) = 0
            end
        end 
    end
    
    
    // Unused inputs and outputs
    assign uio_out = 8'b0;
    assign uio_oe = 8'b0;                       // Input enable for bidirectional pins
    wire _unused = &{ena, ui_in[7:3], 1'b0};

endmodule
