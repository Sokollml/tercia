<?php
/**
 * Plugin Name: Verano — Блюда (CPT)
 * Description: Кастомный тип записи «Блюдо» с таксономией «Категория меню» и мета-полями (цена, метки веган/остро/выбор шефа). Загружается как mu-plugin, поэтому не выключается из админки и переживает смену темы.
 * Author: Verano
 * Version: 1.0.0
 * Text Domain: verano
 *
 * Положить файл в wp-content/mu-plugins/verano-dish-cpt.php
 * (папку mu-plugins создать, если её нет).
 */

if ( ! defined( 'ABSPATH' ) ) {
	exit; // Нет прямого доступа.
}

/**
 * Регистрация типа записи «Блюдо».
 */
function verano_register_dish_cpt() {
	$labels = array(
		'name'                  => __( 'Блюда', 'verano' ),
		'singular_name'         => __( 'Блюдо', 'verano' ),
		'menu_name'             => __( 'Меню (блюда)', 'verano' ),
		'add_new'               => __( 'Добавить блюдо', 'verano' ),
		'add_new_item'          => __( 'Новое блюдо', 'verano' ),
		'edit_item'             => __( 'Редактировать блюдо', 'verano' ),
		'new_item'              => __( 'Новое блюдо', 'verano' ),
		'view_item'             => __( 'Посмотреть блюдо', 'verano' ),
		'search_items'          => __( 'Искать блюда', 'verano' ),
		'not_found'             => __( 'Блюда не найдены', 'verano' ),
		'not_found_in_trash'    => __( 'В корзине блюд нет', 'verano' ),
		'all_items'             => __( 'Все блюда', 'verano' ),
		'featured_image'        => __( 'Фото блюда', 'verano' ),
		'set_featured_image'    => __( 'Задать фото блюда', 'verano' ),
		'remove_featured_image' => __( 'Убрать фото', 'verano' ),
	);

	$args = array(
		'labels'             => $labels,
		'public'             => true,
		'has_archive'        => true,
		'menu_icon'          => 'dashicons-carrot',
		'menu_position'      => 5,
		'show_in_rest'       => true, // Поддержка редактора Gutenberg и REST.
		'supports'           => array( 'title', 'editor', 'thumbnail', 'excerpt', 'page-attributes' ),
		'rewrite'            => array( 'slug' => 'menu-item', 'with_front' => false ),
	);

	register_post_type( 'dish', $args );
}
add_action( 'init', 'verano_register_dish_cpt' );

/**
 * Таксономия «Категория меню» (Закуски, Паста, Из печи, Веган, Десерты, Напитки).
 */
function verano_register_dish_taxonomy() {
	$labels = array(
		'name'              => __( 'Категории меню', 'verano' ),
		'singular_name'     => __( 'Категория меню', 'verano' ),
		'search_items'      => __( 'Искать категории', 'verano' ),
		'all_items'         => __( 'Все категории', 'verano' ),
		'edit_item'         => __( 'Редактировать категорию', 'verano' ),
		'update_item'       => __( 'Обновить категорию', 'verano' ),
		'add_new_item'      => __( 'Добавить категорию', 'verano' ),
		'new_item_name'     => __( 'Название категории', 'verano' ),
		'menu_name'         => __( 'Категории меню', 'verano' ),
	);

	register_taxonomy(
		'dish_category',
		array( 'dish' ),
		array(
			'labels'            => $labels,
			'hierarchical'      => true, // Как рубрики.
			'public'            => true,
			'show_admin_column' => true,
			'show_in_rest'      => true,
			'rewrite'           => array( 'slug' => 'menu-category', 'with_front' => false ),
		)
	);
}
add_action( 'init', 'verano_register_dish_taxonomy' );

/**
 * Список мета-полей блюда: ключ => подпись.
 */
function verano_dish_meta_fields() {
	return array(
		'_verano_price'  => __( 'Цена (например: ₽ 890)', 'verano' ),
		'_verano_vegan'  => __( 'Веган', 'verano' ),
		'_verano_spicy'  => __( 'Остро', 'verano' ),
		'_verano_chef'   => __( 'Выбор шефа', 'verano' ),
	);
}

/**
 * Регистрируем мета-поля для REST / Gutenberg с санитайзом.
 */
function verano_register_dish_meta() {
	register_post_meta( 'dish', '_verano_price', array(
		'type'              => 'string',
		'single'            => true,
		'show_in_rest'      => true,
		'sanitize_callback' => 'sanitize_text_field',
		'auth_callback'     => function () { return current_user_can( 'edit_posts' ); },
	) );

	foreach ( array( '_verano_vegan', '_verano_spicy', '_verano_chef' ) as $flag ) {
		register_post_meta( 'dish', $flag, array(
			'type'              => 'boolean',
			'single'            => true,
			'show_in_rest'      => true,
			'sanitize_callback' => 'rest_sanitize_boolean',
			'auth_callback'     => function () { return current_user_can( 'edit_posts' ); },
		) );
	}
}
add_action( 'init', 'verano_register_dish_meta' );

/**
 * Мета-бокс на экране редактирования блюда (для классического редактора).
 */
function verano_add_dish_metabox() {
	add_meta_box(
		'verano_dish_details',
		__( 'Детали блюда', 'verano' ),
		'verano_render_dish_metabox',
		'dish',
		'side',
		'high'
	);
}
add_action( 'add_meta_boxes', 'verano_add_dish_metabox' );

function verano_render_dish_metabox( $post ) {
	wp_nonce_field( 'verano_save_dish', 'verano_dish_nonce' );

	$price = get_post_meta( $post->ID, '_verano_price', true );
	$vegan = (bool) get_post_meta( $post->ID, '_verano_vegan', true );
	$spicy = (bool) get_post_meta( $post->ID, '_verano_spicy', true );
	$chef  = (bool) get_post_meta( $post->ID, '_verano_chef', true );
	?>
	<p>
		<label for="verano_price"><strong><?php esc_html_e( 'Цена', 'verano' ); ?></strong></label><br>
		<input type="text" id="verano_price" name="verano_price" value="<?php echo esc_attr( $price ); ?>" placeholder="₽ 890" style="width:100%;">
	</p>
	<p><strong><?php esc_html_e( 'Метки', 'verano' ); ?></strong></p>
	<p>
		<label><input type="checkbox" name="verano_vegan" value="1" <?php checked( $vegan ); ?>> <?php esc_html_e( 'Веган', 'verano' ); ?></label><br>
		<label><input type="checkbox" name="verano_spicy" value="1" <?php checked( $spicy ); ?>> <?php esc_html_e( 'Остро', 'verano' ); ?></label><br>
		<label><input type="checkbox" name="verano_chef" value="1" <?php checked( $chef ); ?>> <?php esc_html_e( 'Выбор шефа', 'verano' ); ?></label>
	</p>
	<?php
}

/**
 * Сохранение мета-полей.
 */
function verano_save_dish_meta( $post_id ) {
	if ( ! isset( $_POST['verano_dish_nonce'] ) || ! wp_verify_nonce( sanitize_text_field( wp_unslash( $_POST['verano_dish_nonce'] ) ), 'verano_save_dish' ) ) {
		return;
	}
	if ( defined( 'DOING_AUTOSAVE' ) && DOING_AUTOSAVE ) {
		return;
	}
	if ( ! current_user_can( 'edit_post', $post_id ) ) {
		return;
	}

	$price = isset( $_POST['verano_price'] ) ? sanitize_text_field( wp_unslash( $_POST['verano_price'] ) ) : '';
	update_post_meta( $post_id, '_verano_price', $price );

	update_post_meta( $post_id, '_verano_vegan', isset( $_POST['verano_vegan'] ) ? 1 : 0 );
	update_post_meta( $post_id, '_verano_spicy', isset( $_POST['verano_spicy'] ) ? 1 : 0 );
	update_post_meta( $post_id, '_verano_chef', isset( $_POST['verano_chef'] ) ? 1 : 0 );
}
add_action( 'save_post_dish', 'verano_save_dish_meta' );

/**
 * Колонки в списке блюд: цена + метки.
 */
function verano_dish_columns( $columns ) {
	$new = array();
	foreach ( $columns as $key => $label ) {
		$new[ $key ] = $label;
		if ( 'title' === $key ) {
			$new['verano_price'] = __( 'Цена', 'verano' );
			$new['verano_flags'] = __( 'Метки', 'verano' );
		}
	}
	return $new;
}
add_filter( 'manage_dish_posts_columns', 'verano_dish_columns' );

function verano_dish_column_content( $column, $post_id ) {
	if ( 'verano_price' === $column ) {
		echo esc_html( get_post_meta( $post_id, '_verano_price', true ) );
	}
	if ( 'verano_flags' === $column ) {
		$flags = array();
		if ( get_post_meta( $post_id, '_verano_vegan', true ) ) { $flags[] = __( 'Веган', 'verano' ); }
		if ( get_post_meta( $post_id, '_verano_spicy', true ) ) { $flags[] = __( 'Остро', 'verano' ); }
		if ( get_post_meta( $post_id, '_verano_chef', true ) ) { $flags[] = __( 'Шеф', 'verano' ); }
		echo esc_html( implode( ', ', $flags ) );
	}
}
add_action( 'manage_dish_posts_custom_column', 'verano_dish_column_content', 10, 2 );

/**
 * Сброс правил перезаписи при активации/деактивации плагина не сработает для mu-plugin,
 * поэтому один раз сбрасываем permalinks вручную (Настройки → Постоянные ссылки → Сохранить),
 * либо через флаг ниже при первом запросе в админке.
 */
function verano_maybe_flush_rewrite() {
	if ( is_admin() && ! get_option( 'verano_rewrite_flushed' ) ) {
		verano_register_dish_cpt();
		verano_register_dish_taxonomy();
		flush_rewrite_rules( false );
		update_option( 'verano_rewrite_flushed', 1 );
	}
}
add_action( 'admin_init', 'verano_maybe_flush_rewrite' );
