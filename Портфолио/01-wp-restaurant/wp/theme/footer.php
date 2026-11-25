<?php
/**
 * Подвал сайта.
 *
 * @package Verano
 */

?>
<footer class="site-footer">
	<div class="wrap">
		<div class="footer-grid">
			<div>
				<span class="brand__name"><?php bloginfo( 'name' ); ?></span>
				<p style="margin-top:14px"><?php echo esc_html( get_bloginfo( 'description' ) ); ?></p>
				<div class="socials">
					<a href="#" aria-label="Instagram"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6"><rect x="3" y="3" width="18" height="18" rx="5"/><circle cx="12" cy="12" r="4"/><circle cx="17.5" cy="6.5" r="1" fill="currentColor" stroke="none"/></svg></a>
					<a href="#" aria-label="Facebook"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6"><path d="M15 3h-3a4 4 0 0 0-4 4v3H5v4h3v7h4v-7h3l1-4h-4V7a1 1 0 0 1 1-1h3Z"/></svg></a>
					<a href="#" aria-label="Telegram"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linejoin="round"><path d="M21 4 3 11l5 2 2 6 3-4 5 4Z"/><path d="M8 13l9-6"/></svg></a>
				</div>
			</div>

			<div>
				<h5><?php esc_html_e( 'Навигация', 'verano' ); ?></h5>
				<?php
				if ( has_nav_menu( 'footer' ) ) {
					wp_nav_menu( array(
						'theme_location' => 'footer',
						'container'      => false,
						'menu_class'     => '',
						'depth'          => 1,
					) );
				} else {
					echo '<ul>';
					echo '<li><a href="' . esc_url( home_url( '/' ) ) . '">' . esc_html__( 'Главная', 'verano' ) . '</a></li>';
					echo '<li><a href="' . esc_url( get_post_type_archive_link( 'dish' ) ) . '">' . esc_html__( 'Меню', 'verano' ) . '</a></li>';
					echo '<li><a href="' . esc_url( home_url( '/about/' ) ) . '">' . esc_html__( 'О нас', 'verano' ) . '</a></li>';
					echo '<li><a href="' . esc_url( home_url( '/gallery/' ) ) . '">' . esc_html__( 'Галерея', 'verano' ) . '</a></li>';
					echo '</ul>';
				}
				?>
			</div>

			<div>
				<h5><?php esc_html_e( 'Гостям', 'verano' ); ?></h5>
				<ul>
					<li><a href="<?php echo esc_url( home_url( '/booking/' ) ); ?>"><?php esc_html_e( 'Бронь стола', 'verano' ); ?></a></li>
					<li><a href="<?php echo esc_url( home_url( '/contacts/' ) ); ?>"><?php esc_html_e( 'Контакты', 'verano' ); ?></a></li>
				</ul>
			</div>

			<div>
				<h5><?php esc_html_e( 'Контакты', 'verano' ); ?></h5>
				<ul>
					<li><?php esc_html_e( 'ул. Приморская, 14', 'verano' ); ?></li>
					<li><a href="tel:+78120000000">+7 812 000-00-00</a></li>
					<li><a href="mailto:hello@verano.example">hello@verano.example</a></li>
				</ul>
			</div>
		</div>

		<div class="footer-bottom">
			<span>&copy; <?php echo esc_html( date_i18n( 'Y' ) ); ?> <?php bloginfo( 'name' ); ?>.</span>
			<span><?php esc_html_e( 'Сделано с любовью к средиземноморской кухне', 'verano' ); ?></span>
		</div>
	</div>
</footer>

<?php wp_footer(); ?>
</body>
</html>
