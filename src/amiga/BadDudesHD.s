; Elevator Action AGA slave
	INCDIR	Include:
	INCLUDE	whdload.i
	INCLUDE	whdmacros.i

DEV_MODE

FASTMEMSIZE = $1A0000


	IFD	DEV_MODE
SAVEGAME_SIZE = $0
	ELSE
SAVEGAME_SIZE = $2800    ; size needed for savegame code, not save game data itself
	ENDC

BASE_CHIP = $200
SAVEGAME_FILE_SIZE = $3808   ; wrong
START_CHIP = BASE_CHIP+SAVEGAME_SIZE

_base	SLAVE_HEADER					; ws_security + ws_id
	dc.w	17					; ws_version (was 10)
	dc.w	WHDLF_NoError|WHDLF_EmulTrap|WHDLF_ReqAGA|WHDLF_Req68020
	dc.l	$200000					; ws_basememsize
	dc.l	0					; ws_execinstall
	dc.w	start-_base		; ws_gameloader
	dc.w	_data-_base					; ws_currentdir
	dc.w	0					; ws_dontcache
_keydebug
	dc.b	$0					; ws_keydebug
_keyexit
	dc.b	$59					; ws_keyexit
_expmem
	dc.l	FASTMEMSIZE					; ws_expmem
	dc.w	_name-_base				; ws_name
	dc.w	_copy-_base				; ws_copy
	dc.w	_info-_base				; ws_info
    dc.w    0     ; kickstart name
    dc.l    $0         ; kicksize
    dc.w    $0         ; kickcrc
    dc.w    _config-_base
;---
_config
	dc.b	"C1:X:invincibility:0;"
	dc.b	"C1:X:infinite lives:1;"
	dc.b	"C1:X:infinite time:2;"
	dc.b	"C1:X:super blow power:3;"
	dc.b	"C1:X:cheat keys:4;"
	dc.b    "C2:L:frameskip:auto,none,one,two;"
	IFD		DEV_MODE
	; none: allows double buffering, chip starts at $200, exe in fast
	; simple: no double buffering, chip starts at $60000, exe in 0
	; reloc: no double buffering, chip starts at $60000, exe in fast
	dc.b	"C3:L:debug mode:none,simple,reloc;"
	ENDC
	dc.b    "C4:L:start level:city,truck,sewer,forest,train,cave,boss base;"
	dc.b    "C5:L:difficulty:easy,normal,hard,hardest;"
	dc.b	0

	IFD BARFLY
	DOSCMD	"WDate  >T:date"
	ENDC



DECL_VERSION:MACRO
	dc.b	"1.2"
	IFD BARFLY
		dc.b	" "
		INCBIN	"T:date"
	ENDC
	IFD	DATETIME
		dc.b	" "
		incbin	datetime
	ENDC
	ENDM
_data   dc.b    "data",0
_name	dc.b	'Bad Dudes vs Dragonninja',0
_copy	dc.b	'2025 JOTD',0
_info
    dc.b    "Music by no9",0
	dc.b	0
_kickname   dc.b    0
;--- version id

    dc.b	0
    even
_tag		dc.l	WHDLTAG_CUSTOM3_GET
debug_mode:
	dc.l	0
	dc.l	0

start:
	LEA	_resload(PC),A1
	MOVE.L	A0,(A1)
	move.l	a0,a2


	;setup cache: max cache everywhere
	move.l	#WCPUF_Base_WT|WCPUF_Exp_CB|WCPUF_Slave_CB|WCPUF_IC|WCPUF_DC|WCPUF_BC|WCPUF_SS|WCPUF_SB,d0
	move.l	#WCPUF_All,d1
	jsr	(resload_SetCPU,a2)
	
	lea	(_tag,pc),a0
	jsr	(resload_Control,a2)
    
    lea progstart(pc),a0
    move.l  _expmem(pc),(a0)
	move.l	_expmem(pc),$4

	move.l	_expmem(pc),a7
	add.l	#FASTMEMSIZE-4,a7
	lea	exe(pc),a0
	move.l  progstart(pc),a1
	jsr	(resload_LoadFileDecrunch,a2)
	move.l  progstart(pc),a0
    bsr   _Relocate
	lea		_resload(pc),a0		; note: address of pointer on resload+_savegame_func+_loadgame_func
    move.l  #'WHDL',d0
    move.b  _keyexit(pc),d1
	move.l  progstart(pc),-(a7)
   	IFD	DEV_MODE
	lea	loadgame(pc),a1
	move.l	a1,(4,a0)
	lea	savegame(pc),a1
	move.l	a1,(8,a0)
	ENDC
 
    lea  _custom,a1
    move.w  #$1200,bplcon0(a1)
    move.w  #$0024,bplcon2(a1)
    rts
	
_Relocate	movem.l	d0-d1/a0-a2,-(sp)
        clr.l   -(a7)                   ;TAG_DONE
;        pea     -1                      ;true
;        pea     WHDLTAG_LOADSEG
		move.l	#START_CHIP,d1		| start of program chipmem
		IFD		DEV_MODE
		move.l  debug_mode(pc),d0
		cmp.b	#0,d0
		beq		.1
        move.l  #$60000,d1      ; chip area moved to be able to load program / relocate
.1:
		ENDC
        move.l  d1,-(a7)       ;chip area
        pea     WHDLTAG_CHIPPTR        
        pea     8                       ;8 byte alignment
        pea     WHDLTAG_ALIGN

        move.l  a7,a1                   ;tags	
		move.l	_resload(pc),a2
		jsr	resload_Relocate(a2)
		IFND		CHIP_ONLY
        add.w   #5*4,a7
		ELSE
		addq.w	#4,a7
		ENDC
		
        movem.l	(sp)+,d0-d1/a0-a2
		rts

	IFD	DEV_MODE
; < A0: game RAM
loadgame
    movem.l a0/a2,-(a7)
	move.l	#SAVEGAME_FILE_SIZE,d0	; size of RAM
	lea	BASE_CHIP,a1
	bsr	_sg_load
    movem.l (a7)+,a0/a2
	; D0 success
	rts


; < A0: game ram
savegame
    movem.l a2,-(a7)
;	move.l	trainer(PC),d0
;	bne.s	.skip		;no save on trainer
	lea	BASE_CHIP,a1
	move.l	#SAVEGAME_FILE_SIZE,d0	; size of RAM
	bsr	_sg_save
.skip
    movem.l (a7)+,a2
	rts
	
	
_exit:
	pea	TDREASON_OK
	move.l	_resload(pc),-(a7)
	addq.l	#resload_Abort,(a7)
	rts
	
	include	savegame.s

	ENDC
	
	
_resload:
	dc.l	0
progstart
    dc.l    0
exe
	dc.b	"baddudes",0
	