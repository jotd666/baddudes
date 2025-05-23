	.ifdef	RELEASE
	.macro	BREAKPOINT comment
	.endm
	.else
	* amiga specific
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
OPT_SKIP_TITLE = 0		        | DO NOT CHANGE
OPT_SKIP_RONNIE_THANKS = 0		| DO NOT CHANGE
OPT_NO_SECOND_PLAYER = 1		| DO NOT CHANGE
	.else
OPT_SKIP_TITLE = 0
OPT_SKIP_RONNIE_THANKS = 0
OPT_NO_SECOND_PLAYER = 1
	.endif
	
CTX_UNKNOWN = 0
CTX_INTRO = 1
CTX_HIGH_SCORE = 2
CTX_GAME_INTRO = 3
CTX_GAME = 4
CTX_END_SEQUENCE_1 = 5
CTX_END_SEQUENCE_2 = 6

