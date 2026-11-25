<?php
/**
 * Custom post type "Отзыв" (testimonial) and its meta fields.
 *
 * @package ReviewsBlock
 */

if ( ! defined( 'ABSPATH' ) ) {
	exit;
}

/**
 * Registers the testimonial CPT and meta.
 */
class Reviews_Block_CPT {

	const POST_TYPE = 'testimonial';

	/**
	 * Hook registration.
	 */
	public function register() {
		$this->register_post_type();
		$this->register_meta();

		add_action( 'add_meta_boxes', array( $this, 'add_meta_boxes' ) );
		add_action( 'save_post_' . self::POST_TYPE, array( $this, 'save_meta' ), 10, 2 );
	}

	/**
	 * Register the "testimonial" post type.
	 */
	public function register_post_type() {
		$labels = array(
			'name'                  => __( 'Отзывы', 'reviews-block' ),
			'singular_name'         => __( 'Отзыв', 'reviews-block' ),
			'menu_name'             => __( 'Отзывы', 'reviews-block' ),
			'add_new'               => __( 'Добавить отзыв', 'reviews-block' ),
			'add_new_item'          => __( 'Добавить новый отзыв', 'reviews-block' ),
			'edit_item'             => __( 'Редактировать отзыв', 'reviews-block' ),
			'new_item'              => __( 'Новый отзыв', 'reviews-block' ),
			'view_item'             => __( 'Просмотреть отзыв', 'reviews-block' ),
			'search_items'          => __( 'Искать отзывы', 'reviews-block' ),
			'not_found'             => __( 'Отзывы не найдены', 'reviews-block' ),
			'not_found_in_trash'    => __( 'В корзине отзывов нет', 'reviews-block' ),
			'all_items'             => __( 'Все отзывы', 'reviews-block' ),
			'featured_image'        => __( 'Фото автора', 'reviews-block' ),
			'set_featured_image'    => __( 'Задать фото автора', 'reviews-block' ),
			'remove_featured_image' => __( 'Удалить фото автора', 'reviews-block' ),
			'use_featured_image'    => __( 'Использовать как фото автора', 'reviews-block' ),
		);

		$args = array(
			'labels'              => $labels,
			'public'              => true,
			'has_archive'         => true,
			'show_in_rest'        => true, // Needed for Gutenberg + REST queries.
			'menu_icon'           => 'dashicons-format-quote',
			'menu_position'       => 25,
			'supports'            => array( 'title', 'editor', 'thumbnail', 'custom-fields' ),
			'rewrite'             => array( 'slug' => 'testimonials' ),
			'capability_type'     => 'post',
			'exclude_from_search' => false,
		);

		register_post_type( self::POST_TYPE, $args );
	}

	/**
	 * Register meta so it is exposed in the REST API (show_in_rest) and Gutenberg.
	 */
	public function register_meta() {
		register_post_meta(
			self::POST_TYPE,
			'_reviews_block_rating',
			array(
				'type'              => 'integer',
				'description'       => __( 'Оценка от 1 до 5', 'reviews-block' ),
				'single'            => true,
				'default'           => 5,
				'show_in_rest'      => true,
				'sanitize_callback' => array( $this, 'sanitize_rating' ),
				'auth_callback'     => function () {
					return current_user_can( 'edit_posts' );
				},
			)
		);

		register_post_meta(
			self::POST_TYPE,
			'_reviews_block_company',
			array(
				'type'              => 'string',
				'description'       => __( 'Компания / должность', 'reviews-block' ),
				'single'            => true,
				'default'           => '',
				'show_in_rest'      => true,
				'sanitize_callback' => 'sanitize_text_field',
				'auth_callback'     => function () {
					return current_user_can( 'edit_posts' );
				},
			)
		);
	}

	/**
	 * Clamp the rating to 1..5.
	 *
	 * @param mixed $value Raw value.
	 * @return int
	 */
	public function sanitize_rating( $value ) {
		$value = (int) $value;
		if ( $value < 1 ) {
			$value = 1;
		}
		if ( $value > 5 ) {
			$value = 5;
		}
		return $value;
	}

	/**
	 * Add the classic meta box (works even if the CPT uses the classic editor).
	 */
	public function add_meta_boxes() {
		add_meta_box(
			'reviews_block_details',
			__( 'Детали отзыва', 'reviews-block' ),
			array( $this, 'render_meta_box' ),
			self::POST_TYPE,
			'side',
			'high'
		);
	}

	/**
	 * Render the meta box UI.
	 *
	 * @param WP_Post $post Current post.
	 */
	public function render_meta_box( $post ) {
		wp_nonce_field( 'reviews_block_save_meta', 'reviews_block_nonce' );

		$rating  = (int) get_post_meta( $post->ID, '_reviews_block_rating', true );
		$company = (string) get_post_meta( $post->ID, '_reviews_block_company', true );
		if ( $rating < 1 || $rating > 5 ) {
			$rating = 5;
		}
		?>
		<p>
			<label for="reviews_block_rating"><strong><?php esc_html_e( 'Оценка (1–5)', 'reviews-block' ); ?></strong></label><br />
			<select name="reviews_block_rating" id="reviews_block_rating" style="width:100%;">
				<?php for ( $i = 1; $i <= 5; $i++ ) : ?>
					<option value="<?php echo esc_attr( $i ); ?>" <?php selected( $rating, $i ); ?>>
						<?php echo esc_html( str_repeat( '★', $i ) . str_repeat( '☆', 5 - $i ) ); ?>
					</option>
				<?php endfor; ?>
			</select>
		</p>
		<p>
			<label for="reviews_block_company"><strong><?php esc_html_e( 'Компания / должность', 'reviews-block' ); ?></strong></label><br />
			<input type="text" name="reviews_block_company" id="reviews_block_company"
				value="<?php echo esc_attr( $company ); ?>" style="width:100%;"
				placeholder="<?php esc_attr_e( 'Например: CEO, Acme Inc.', 'reviews-block' ); ?>" />
		</p>
		<p class="description">
			<?php esc_html_e( 'Фото автора задаётся через «Изображение записи» (featured image).', 'reviews-block' ); ?>
		</p>
		<?php
	}

	/**
	 * Persist meta on save with nonce + capability checks and sanitization.
	 *
	 * @param int     $post_id Post ID.
	 * @param WP_Post $post    Post object.
	 */
	public function save_meta( $post_id, $post ) {
		// Bail on autosave / revisions.
		if ( defined( 'DOING_AUTOSAVE' ) && DOING_AUTOSAVE ) {
			return;
		}
		if ( wp_is_post_revision( $post_id ) ) {
			return;
		}

		// Nonce check.
		if ( ! isset( $_POST['reviews_block_nonce'] )
			|| ! wp_verify_nonce( sanitize_key( wp_unslash( $_POST['reviews_block_nonce'] ) ), 'reviews_block_save_meta' ) ) {
			return;
		}

		// Capability check.
		if ( ! current_user_can( 'edit_post', $post_id ) ) {
			return;
		}

		// Rating.
		if ( isset( $_POST['reviews_block_rating'] ) ) {
			$rating = $this->sanitize_rating( wp_unslash( $_POST['reviews_block_rating'] ) );
			update_post_meta( $post_id, '_reviews_block_rating', $rating );
		}

		// Company.
		if ( isset( $_POST['reviews_block_company'] ) ) {
			$company = sanitize_text_field( wp_unslash( $_POST['reviews_block_company'] ) );
			update_post_meta( $post_id, '_reviews_block_company', $company );
		}
	}
}
