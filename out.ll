; ModuleID = 'out.ll'

define i32 @main() {
entry:
	%out_0x0 = icmp eq i32 1, 2
	%out_0x1 = icmp neq i1 %out_0x0, 0
	br i1 %out_0x1, label %out_0x2_then, label %out_0x3_iffail
out_0x2_then:
	%out_0x5 = add i32 1, 2
	br label out_0x6_ifdone
out_0x3_iffail:
	%out_0x7 = add i32 3, 4
	br label out_0x6_ifdone
out_0x6_ifdone:
	ret i32 42
}

