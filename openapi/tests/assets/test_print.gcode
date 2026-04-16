; Basic test print for OpenAPI conformance testing
; Designed to run long enough for pause/resume testing
G28 ; Home all axes
G90 ; Absolute positioning
G1 Z5 F600 ; Raise Z
; Repeated pattern to ensure print takes long enough
G1 X10 Y10 F300
G1 X50 Y10 F300
G1 X50 Y50 F300
G1 X10 Y50 F300
G1 X10 Y10 F300
G4 P2000 ; Dwell 2 seconds
G1 X50 Y10 F300
G1 X50 Y50 F300
G1 X10 Y50 F300
G1 X10 Y10 F300
G4 P2000 ; Dwell 2 seconds
G1 X50 Y10 F300
G1 X50 Y50 F300
G1 X10 Y50 F300
G1 X10 Y10 F300
G4 P2000 ; Dwell 2 seconds
G1 X50 Y10 F300
G1 X50 Y50 F300
G1 X10 Y50 F300
G1 X10 Y10 F300
G4 P2000 ; Dwell 2 seconds
G1 X50 Y10 F300
G1 X50 Y50 F300
G1 X10 Y50 F300
G1 X10 Y10 F300
G4 P2000 ; Dwell 2 seconds
G1 Z10 F600 ; Raise Z
G28 X Y ; Home X and Y
M84 ; Disable motors
