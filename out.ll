; ModuleID = 'out.ll'

define i32 @main() {
entry:
	%out_0x0 = icmp eq i1 1, 1
	br i1 %out_0x0, label %out_0x1_then, label %out_0x2_iffail
out_0x1_then:
	%out_0x4 = add i32 1, 2
	br label out_0x5_ifdone
out_0x2_iffail:
	%out_0x6 = add i32 3, 4
	br label out_0x5_ifdone
out_0x5_ifdone:
	ret i32 42
}

