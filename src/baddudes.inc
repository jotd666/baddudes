	.ifdef	RELEASE
	.macro	BREAKPOINT comment
	.endm
	.else
	.macro	BREAKPOINT comment
	move.l	a0,-(a7)
	lea		comment\@(pc),a0
	jbsr	osd_break
	move.l	(a7)+,a0
	jra		next\@
comment\@:
	.asciz	"\comment"
	.align	2
next\@:
	.endm
	.endc

	.ifdef	RELEASE
OPT_SKIP_TITLE = 0
	.else
OPT_SKIP_TITLE = 0
	.endif
	
CTX_UNKNOWN = 0
CTX_INTRO = 1
CTX_HIGH_SCORE = 2

