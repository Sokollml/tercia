<?php
/**
 * Plugin Name: FORMA Core
 * Description: Кастомные типы записей «Занятие» и «Тренер», таксономия «Тип тренировки», мета-поля и шорткоды для студии FORMA. Вынесено в mu-plugin, чтобы данные не зависели от активной темы.
 * Version:     1.0.0
 * Author:      FORMA
 * Text Domain: forma
 *
 * ВАЖНО: mu-plugins загружаются автоматически. Файл кладётся в wp-content/mu-plugins/.
 * Так контент (расписание, тренеры) остаётся в базе даже при смене темы.
 */

if ( ! defined( 'ABSPATH' ) ) { exit; }

/* ============================================================
 * 1. Кастомные типы записей
 * ============================================================ */
add_action( 'init', function () {

	// --- Тип «Тренер» (trainer) ---
	register_post_type( 'trainer', array(
		'labels' => array(
			'name'               => __( 'Тренеры', 'forma' ),
			'singular_name'      => __( 'Тренер', 'forma' ),
			'add_new'            => __( 'Добавить тренера', 'forma' ),
			'add_new_item'       => __( 'Новый тренер', 'forma' ),
			'edit_item'          => __( 'Редактировать тренера', 'forma' ),
			'all_items'          => __( 'Все тренеры', 'forma' ),
			'menu_name'          => __( 'Тренеры', 'forma' ),
		),
		'public'       => true,
		'has_archive'  => true,
		'menu_icon'    => 'dashicons-groups',
		'menu_position'=> 22,
		'rewrite'      => array( 'slug' => 'trainers' ),
		'supports'     => array( 'title', 'editor', 'thumbnail' ), // title = имя, editor = био, thumbnail = фото
		'show_in_rest' => true, // Gutenberg + REST (нужно для фронтенда/Polylang)
	) );

	// --- Тип «Занятие» (class) ---
	register_post_type( 'class', array(
		'labels' => array(
			'name'               => __( 'Занятия', 'forma' ),
			'singular_name'      => __( 'Занятие', 'forma' ),
			'add_new'            => __( 'Добавить занятие', 'forma' ),
			'add_new_item'       => __( 'Новое занятие', 'forma' ),
			'edit_item'          => __( 'Редактировать занятие', 'forma' ),
			'all_items'          => __( 'Все занятия', 'forma' ),
			'menu_name'          => __( 'Расписание', 'forma' ),
		),
		'public'       => true,
		'has_archive'  => true,
		'menu_icon'    => 'dashicons-calendar-alt',
		'menu_position'=> 21,
		'rewrite'      => array( 'slug' => 'schedule' ),
		'supports'     => array( 'title', 'editor' ), // title = название занятия
		'show_in_rest' => true,
	) );

	// --- Таксономия «Тип тренировки» (class_type): Сила / Кардио / Тело и ум / Танцы ---
	register_taxonomy( 'class_type', array( 'class' ), array(
		'labels' => array(
			'name'          => __( 'Типы тренировок', 'forma' ),
			'singular_name' => __( 'Тип тренировки', 'forma' ),
			'menu_name'     => __( 'Типы', 'forma' ),
		),
		'public'            => true,
		'hierarchical'      => true,
		'show_admin_column' => true,
		'show_in_rest'      => true,
	) );
} );

/* ============================================================
 * 2. Мета-поля
 *   Занятие: день недели, время, тренер
 *   Тренер:  специализация (фото = thumbnail, имя = title, био = editor)
 * ============================================================ */
add_action( 'init', function () {
	register_post_meta( 'class', '_forma_day',  array( 'type' => 'string', 'single' => true, 'show_in_rest' => true, 'sanitize_callback' => 'sanitize_text_field' ) );
	register_post_meta( 'class', '_forma_time', array( 'type' => 'string', 'single' => true, 'show_in_rest' => true, 'sanitize_callback' => 'sanitize_text_field' ) );
	register_post_meta( 'class', '_forma_trainer_id', array( 'type' => 'integer', 'single' => true, 'show_in_rest' => true, 'sanitize_callback' => 'absint' ) );

	register_post_meta( 'trainer', '_forma_spec', array( 'type' => 'string', 'single' => true, 'show_in_rest' => true, 'sanitize_callback' => 'sanitize_text_field' ) );
} );

/* Дни недели — единый справочник */
function forma_days() {
	return array(
		'mon' => __( 'Понедельник', 'forma' ),
		'tue' => __( 'Вторник', 'forma' ),
		'wed' => __( 'Среда', 'forma' ),
		'thu' => __( 'Четверг', 'forma' ),
		'fri' => __( 'Пятница', 'forma' ),
		'sat' => __( 'Суббота', 'forma' ),
		'sun' => __( 'Воскресенье', 'forma' ),
	);
}

/* ============================================================
 * 3. Мета-боксы в админке (без внешних плагинов)
 * ============================================================ */
add_action( 'add_meta_boxes', function () {
	add_meta_box( 'forma_class_meta', __( 'Детали занятия', 'forma' ), 'forma_class_metabox', 'class', 'side', 'high' );
	add_meta_box( 'forma_trainer_meta', __( 'Специализация', 'forma' ), 'forma_trainer_metabox', 'trainer', 'side', 'high' );
} );

function forma_class_metabox( $post ) {
	wp_nonce_field( 'forma_class_save', 'forma_class_nonce' );
	$day     = get_post_meta( $post->ID, '_forma_day', true );
	$time    = get_post_meta( $post->ID, '_forma_time', true );
	$trainer = (int) get_post_meta( $post->ID, '_forma_trainer_id', true );
	$trainers = get_posts( array( 'post_type' => 'trainer', 'numberposts' => -1, 'orderby' => 'title', 'order' => 'ASC' ) );
	?>
	<p><label><strong><?php esc_html_e( 'День недели', 'forma' ); ?></strong><br>
		<select name="forma_day" style="width:100%">
			<?php foreach ( forma_days() as $k => $label ) : ?>
				<option value="<?php echo esc_attr( $k ); ?>" <?php selected( $day, $k ); ?>><?php echo esc_html( $label ); ?></option>
			<?php endforeach; ?>
		</select></label></p>
	<p><label><strong><?php esc_html_e( 'Время (ЧЧ:ММ)', 'forma' ); ?></strong><br>
		<input type="time" name="forma_time" value="<?php echo esc_attr( $time ); ?>" style="width:100%"></label></p>
	<p><label><strong><?php esc_html_e( 'Тренер', 'forma' ); ?></strong><br>
		<select name="forma_trainer_id" style="width:100%">
			<option value="0"><?php esc_html_e( '— не выбран —', 'forma' ); ?></option>
			<?php foreach ( $trainers as $t ) : ?>
				<option value="<?php echo esc_attr( $t->ID ); ?>" <?php selected( $trainer, $t->ID ); ?>><?php echo esc_html( $t->post_title ); ?></option>
			<?php endforeach; ?>
		</select></label></p>
	<p class="description"><?php esc_html_e( 'Тип тренировки задаётся справа в блоке «Типы».', 'forma' ); ?></p>
	<?php
}

function forma_trainer_metabox( $post ) {
	wp_nonce_field( 'forma_trainer_save', 'forma_trainer_nonce' );
	$spec = get_post_meta( $post->ID, '_forma_spec', true );
	?>
	<p><label><strong><?php esc_html_e( 'Специализация', 'forma' ); ?></strong><br>
		<input type="text" name="forma_spec" value="<?php echo esc_attr( $spec ); ?>" style="width:100%" placeholder="<?php esc_attr_e( 'например: Йога, пилатес', 'forma' ); ?>"></label></p>
	<p class="description"><?php esc_html_e( 'Имя — это заголовок записи, фото — «Изображение записи», био — основной текст.', 'forma' ); ?></p>
	<?php
}

add_action( 'save_post_class', function ( $post_id ) {
	if ( ! isset( $_POST['forma_class_nonce'] ) || ! wp_verify_nonce( $_POST['forma_class_nonce'], 'forma_class_save' ) ) { return; }
	if ( defined( 'DOING_AUTOSAVE' ) && DOING_AUTOSAVE ) { return; }
	if ( ! current_user_can( 'edit_post', $post_id ) ) { return; }
	update_post_meta( $post_id, '_forma_day', sanitize_text_field( $_POST['forma_day'] ?? '' ) );
	update_post_meta( $post_id, '_forma_time', sanitize_text_field( $_POST['forma_time'] ?? '' ) );
	update_post_meta( $post_id, '_forma_trainer_id', absint( $_POST['forma_trainer_id'] ?? 0 ) );
} );

add_action( 'save_post_trainer', function ( $post_id ) {
	if ( ! isset( $_POST['forma_trainer_nonce'] ) || ! wp_verify_nonce( $_POST['forma_trainer_nonce'], 'forma_trainer_save' ) ) { return; }
	if ( defined( 'DOING_AUTOSAVE' ) && DOING_AUTOSAVE ) { return; }
	if ( ! current_user_can( 'edit_post', $post_id ) ) { return; }
	update_post_meta( $post_id, '_forma_spec', sanitize_text_field( $_POST['forma_spec'] ?? '' ) );
} );

/* Колонки в списке занятий — удобно администратору */
add_filter( 'manage_class_posts_columns', function ( $cols ) {
	$cols['forma_day']  = __( 'День', 'forma' );
	$cols['forma_time'] = __( 'Время', 'forma' );
	return $cols;
} );
add_action( 'manage_class_posts_custom_column', function ( $col, $post_id ) {
	if ( 'forma_day' === $col ) {
		$days = forma_days();
		$d = get_post_meta( $post_id, '_forma_day', true );
		echo esc_html( $days[ $d ] ?? '—' );
	}
	if ( 'forma_time' === $col ) {
		echo esc_html( get_post_meta( $post_id, '_forma_time', true ) ?: '—' );
	}
}, 10, 2 );

/* ============================================================
 * 4. Шорткоды для вывода на страницах / в Elementor
 *    [forma_schedule]  — сетка расписания по дням
 *    [forma_trainers]  — карточки тренеров
 * ============================================================ */
add_shortcode( 'forma_schedule', function () {
	$days = forma_days();
	$q = new WP_Query( array(
		'post_type'      => 'class',
		'posts_per_page' => -1,
		'meta_key'       => '_forma_time',
		'orderby'        => 'meta_value',
		'order'          => 'ASC',
	) );

	// Группируем занятия по дням
	$grid = array();
	foreach ( $q->posts as $p ) {
		$d = get_post_meta( $p->ID, '_forma_day', true );
		$grid[ $d ][] = $p;
	}
	wp_reset_postdata();

	ob_start();
	echo '<div class="forma-schedule">';
	foreach ( $days as $key => $label ) {
		if ( empty( $grid[ $key ] ) ) { continue; }
		echo '<div class="forma-day"><h3>' . esc_html( $label ) . '</h3>';
		foreach ( $grid[ $key ] as $c ) {
			$time = get_post_meta( $c->ID, '_forma_time', true );
			$tid  = (int) get_post_meta( $c->ID, '_forma_trainer_id', true );
			$coach = $tid ? get_the_title( $tid ) : '';
			$types = get_the_term_list( $c->ID, 'class_type', '', ', ' );
			echo '<div class="forma-class">';
			echo '<span class="t">' . esc_html( $time ) . '</span> ';
			echo '<b>' . esc_html( get_the_title( $c ) ) . '</b>';
			if ( $coach ) { echo '<small> · ' . esc_html( $coach ) . '</small>'; }
			if ( $types ) { echo '<span class="type">' . wp_kses_post( $types ) . '</span>'; }
			echo '</div>';
		}
		echo '</div>';
	}
	echo '</div>';
	return ob_get_clean();
} );

add_shortcode( 'forma_trainers', function () {
	$q = new WP_Query( array( 'post_type' => 'trainer', 'posts_per_page' => -1, 'orderby' => 'title', 'order' => 'ASC' ) );
	ob_start();
	echo '<div class="forma-trainers">';
	while ( $q->have_posts() ) : $q->the_post();
		$spec = get_post_meta( get_the_ID(), '_forma_spec', true );
		echo '<article class="forma-trainer">';
		if ( has_post_thumbnail() ) {
			echo '<div class="photo">' . get_the_post_thumbnail( get_the_ID(), 'medium_large' ) . '</div>';
		}
		echo '<div class="body"><h3>' . esc_html( get_the_title() ) . '</h3>';
		if ( $spec ) { echo '<div class="role">' . esc_html( $spec ) . '</div>'; }
		echo '<div class="bio">' . wp_kses_post( wpautop( get_the_content() ) ) . '</div>';
		echo '</div></article>';
	endwhile;
	wp_reset_postdata();
	echo '</div>';
	return ob_get_clean();
} );

/* ============================================================
 * 5. Сброс правил ЧПУ при активации структуры (разово)
 * ============================================================ */
add_action( 'after_switch_theme', 'flush_rewrite_rules' );
