#include <string.h>
#include "consts.h"
#include "generals.h"
#include "diagnostic.h"
#include "modes/setup.h"
#include "modes/menufuncs.h"
#include "unk/unk4.h"
#include "unk/unk4_1.h"

// FUNCTION: GY454XE  Re 09712
// FUNCTION: GY455XE  Im 0A036
// FUNCTION: GY460XF  Im 099BE
// FUNCTION: GY465XG  Im 095AA
void main(void) {
	signed char need_render;
	char fetch_next;

	memset(&stack_start, 90, 800);
	f_046E0();
	delay(952);
	cursor_noflash = 0;
	if (need_reset()) reset_all();
	f_03558();
	set_contrast2_0();
	set_scr_normal();
	diag_factory_test();
	if (!diag_init_check()) diagnostic_mode();
	if (mode == MODE_EQN || mode == MODE_INEQ || mode == MODE_RATIO) {
		d_080FE = 0;
		last_key_keycode = 0;
		fill_screen(0x200);
	}

	if (mode == MODE_EQN) table_mode = TABLE_EQN;
	else if (mode == MODE_INEQ) table_mode = TABLE_INEQ;
	else if (mode == MODE_RATIO) table_mode = TABLE_RATIO;
	f_112EA();

	fetch_next = 0;
	while (1) {
		if (fetch_next) {
			set_scr_normal();
			set_keycode(getkeycode(1));
			if (last_key_keycode == K_MODE) screen_state = 1;
			else if (last_key_keycode == K_SETUP) screen_state = 2;
			else if (K_SD <= last_key_keycode && last_key_keycode <= K_VERIFY) screen_state = 3;
			else if (last_key_keycode == K_CALC) {
				if (f_09D84()) continue;
				if (mode != MODE_COMP && mode != MODE_CMPLX) continue;
				f_09D54(TABLE_CALC);
			}
			else if (last_key_keycode == K_SOLVE) {
				if (f_09D84()) continue;
				if (mode != MODE_COMP) continue;
				f_09D54(TABLE_SOLVE);
			}
			else screen_state = 0;
		}
		fetch_next = 1;
		if (screen_state) {
			switch (screen_state) {
				case 1:
					d_08126 = 0;
					need_render = mode_menu();
					break;
				case 2:
					d_08126 = 0;
					if (need_render = setup_menu()) {
						f_044D2();
						if (table_mode & (1 << 4)) f_044B6();
					}
					break;
				case 3:
					need_render = f_09014();
					if (need_render > 0) force_nochar = 0;
					break;
			}
			if (!need_render) render();
			else fetch_next = 0;
			screen_state = 0;
			continue;
		}
		if (f_0B6B6()) fetch_next = f_09962(0);
		else {
			char tm = table_mode;
			if (tm != TABLE_EQN && tm != TABLE_INEQ && tm != TABLE_RATIO && last_key_keycode == K_AC) {
				table_mode = TABLE_NONE;
				f_0B8B8(1);
				fetch_next = 0;
			} else if (tm == TABLE_STAT_TABLE) {
				table_stat_handler();
				fetch_next = 1;
			}
			else if (tm == TABLE_MATRIX) fetch_next = table_mat_handler(need_render);
			else if (tm == TABLE_VECTOR) fetch_next = table_vct_handler(need_render);
			else if (tm == TABLE_EQN) fetch_next = table_eqn_handler(need_render);
			else if (tm == TABLE_RANGE) fetch_next = table_range_handler(need_render);
			else if (tm == TABLE_CALC) fetch_next = calc_solve_handler(need_render);
			else if (tm == TABLE_SOLVE) fetch_next = calc_solve_handler(need_render);
#if ENABLE_INEQ == 1
			else if (tm == TABLE_INEQ) fetch_next = table_ineq_handler(need_render);
#endif
#if ENABLE_RATIO == 1
			else if (tm == TABLE_RATIO) fetch_next = table_ratio_handler(need_render);
#endif
		}
		render();
	}
}
