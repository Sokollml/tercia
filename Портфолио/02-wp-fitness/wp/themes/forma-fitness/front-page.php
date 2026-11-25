<?php
/**
 * Главная страница.
 * Если назначена статическая главная и подключён Elementor — отдаём его контент.
 * Иначе показываем встроенный лендинг с расписанием и тренерами.
 * @package forma-fitness
 */
if ( ! defined( 'ABSPATH' ) ) { exit; }
get_header();

// Отдать управление Elementor, если он рисует главную
if ( function_exists( 'elementor_theme_do_location' ) && elementor_theme_do_location( 'single' ) ) {
	get_footer();
	return;
}
?>

<section class="page-hero">
	<div class="wrap">
		<span class="eyebrow"><?php forma_e( 'Студия функционального фитнеса' ); ?></span>
		<h1><?php esc_html_e( 'Двигайся сильнее каждый день', 'forma' ); ?></h1>
		<p style="color:#a9a99c;max-width:56ch"><?php esc_html_e( 'Групповые и персональные тренировки в центре города. Живое сообщество и тренеры, которые ведут вас к результату.', 'forma' ); ?></p>
		<p><a class="btn btn--accent" href="<?php echo esc_url( home_url( '/contacts/' ) ); ?>"><?php forma_e( 'Записаться на пробное' ); ?></a></p>
	</div>
</section>

<section>
	<div class="wrap">
		<span class="eyebrow"><?php esc_html_e( 'Неделя в студии', 'forma' ); ?></span>
		<h2><?php esc_html_e( 'Расписание', 'forma' ); ?></h2>
		<?php echo do_shortcode( '[forma_schedule]' ); ?>
	</div>
</section>

<section>
	<div class="wrap">
		<span class="eyebrow"><?php esc_html_e( 'Команда', 'forma' ); ?></span>
		<h2><?php esc_html_e( 'Наши тренеры', 'forma' ); ?></h2>
		<?php echo do_shortcode( '[forma_trainers]' ); ?>
	</div>
</section>

<?php get_footer(); ?>
