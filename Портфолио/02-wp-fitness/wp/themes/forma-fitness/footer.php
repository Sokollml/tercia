<?php
/**
 * Подвал сайта.
 * @package forma-fitness
 */
if ( ! defined( 'ABSPATH' ) ) { exit; }
?>
</main><!-- #content -->

<footer class="site-footer">
	<div class="wrap">
		<?php if ( is_active_sidebar( 'footer-1' ) ) : ?>
			<div class="footer-cols">
				<?php dynamic_sidebar( 'footer-1' ); ?>
			</div>
		<?php else : ?>
			<div class="footer-cols">
				<div>
					<div class="brand"><?php bloginfo( 'name' ); ?></div>
					<p><?php echo esc_html( get_bloginfo( 'description' ) ?: 'Студия функционального фитнеса.' ); ?></p>
				</div>
				<div class="footer-col">
					<h4><?php esc_html_e( 'Контакты', 'forma' ); ?></h4>
					<a href="tel:+74951234567">+7 (495) 123-45-67</a>
					<a href="mailto:hello@forma-studio.ru">hello@forma-studio.ru</a>
				</div>
				<div class="footer-col">
					<h4><?php esc_html_e( 'Часы работы', 'forma' ); ?></h4>
					<a><?php esc_html_e( 'Пн–Пт: 07:00–23:00', 'forma' ); ?></a>
					<a><?php esc_html_e( 'Сб–Вс: 09:00–21:00', 'forma' ); ?></a>
				</div>
			</div>
		<?php endif; ?>

		<div class="footer-bottom">
			© <?php echo esc_html( date( 'Y' ) ); ?> <?php bloginfo( 'name' ); ?>. <?php esc_html_e( 'Все права защищены.', 'forma' ); ?>
		</div>
	</div>
</footer>

<?php wp_footer(); ?>
</body>
</html>
