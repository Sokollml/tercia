/**
 * Editor script for the reviews-block/testimonials block.
 * Written in plain JS (no JSX) so the plugin needs no build step.
 *
 * @package ReviewsBlock
 */
( function ( wp ) {
	'use strict';

	var el = wp.element.createElement;
	var __ = wp.i18n.__;
	var registerBlockType = wp.blocks.registerBlockType;
	var useBlockProps = wp.blockEditor.useBlockProps;
	var InspectorControls = wp.blockEditor.InspectorControls;
	var ServerSideRender = wp.serverSideRender;

	var PanelBody = wp.components.PanelBody;
	var RangeControl = wp.components.RangeControl;
	var SelectControl = wp.components.SelectControl;
	var ToggleControl = wp.components.ToggleControl;

	registerBlockType( 'reviews-block/testimonials', {
		edit: function ( props ) {
			var attributes = props.attributes;
			var setAttributes = props.setAttributes;
			var blockProps = useBlockProps();

			var controls = el(
				InspectorControls,
				{ key: 'inspector' },
				el(
					PanelBody,
					{ title: __( 'Настройки отзывов', 'reviews-block' ), initialOpen: true },
					el( RangeControl, {
						label: __( 'Количество отзывов', 'reviews-block' ),
						value: attributes.count,
						onChange: function ( value ) {
							setAttributes( { count: value } );
						},
						min: 1,
						max: 24,
					} ),
					el( SelectControl, {
						label: __( 'Вид', 'reviews-block' ),
						value: attributes.layout,
						options: [
							{ label: __( 'Карусель', 'reviews-block' ), value: 'carousel' },
							{ label: __( 'Сетка', 'reviews-block' ), value: 'grid' },
						],
						onChange: function ( value ) {
							setAttributes( { layout: value } );
						},
					} ),
					attributes.layout === 'carousel'
						? el( ToggleControl, {
								label: __( 'Автопрокрутка', 'reviews-block' ),
								checked: !! attributes.autoplay,
								onChange: function ( value ) {
									setAttributes( { autoplay: value } );
								},
						  } )
						: null,
					attributes.layout === 'carousel' && attributes.autoplay
						? el( RangeControl, {
								label: __( 'Интервал, мс', 'reviews-block' ),
								value: attributes.interval,
								onChange: function ( value ) {
									setAttributes( { interval: value } );
								},
								min: 2000,
								max: 15000,
								step: 500,
						  } )
						: null
				)
			);

			var preview = el(
				'div',
				blockProps,
				el( ServerSideRender, {
					block: 'reviews-block/testimonials',
					attributes: attributes,
				} )
			);

			return [ controls, preview ];
		},

		// Dynamic block: rendering is done in PHP.
		save: function () {
			return null;
		},
	} );
} )( window.wp );
