<?php
/**
 * Архив «Занятия» — страница расписания /schedule/.
 * @package forma-fitness
 */
if ( ! defined( 'ABSPATH' ) ) { exit; }
get_header(); ?>

<section class="page-hero">
	<div class="wrap">
		<span class="eyebrow"><?php esc_html_e( 'Неделя в студии', 'forma' ); ?></span>
		<h1><?php esc_html_e( 'Расписание занятий', 'forma' ); ?></h1>
		<p style="color:#a9a99c;max-width:60ch"><?php esc_html_e( 'День, время, тренер и тип тренировки. Сетка обновляется из админки: добавили занятие — оно появилось на сайте.', 'forma' ); ?></p>
	</div>
</section>

<section>
	<div class="wrap">
		<?php echo do_shortcode( '[forma_schedule]' ); ?>
	</div>
</section>

<?php get_footer(); ?>
