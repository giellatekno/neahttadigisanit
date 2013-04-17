<?php
/*
Plugin Name: Neahttadigisánit
Plugin URI: http://sanit.oahpa.no
Description: A plugin for providing access to dictionaries via clicking.
Version: 0.1.0
Author: Ryan Johnson / Giellatekno
Author URI: http://giellatekno.uit.no/
License: GPL2
*/

function load_dict_css () {
    wp_enqueue_style( 'my_style'
                    , plugins_url('/jquery.neahttadigisanit.css', __FILE__)
                    );
}

function load_dict_scripts () {
    // NOTE: probably already available wp_enqueue_script('jquery');

    wp_enqueue_script( 'gt-ns-jquery'
                     , plugins_url('/jquery.neahttadigisanit.js', __FILE__)
                     , array('jquery')
                     , '1.7.2'
                     ) ;

    wp_enqueue_script( 'gt-ns-main'
                     , plugins_url('/main.js', __FILE__)
                     , array('jquery', 'gt-ns-jquery')
                     ) ;

    $plugin_paths = array(
        'spinner' => plugins_url('/img/spinner.gif', __FILE__),
    ) ;

    wp_localize_script( 'gt-ns-main', 
                        'plugin_paths', 
                        $plugin_paths
                        ) ;

}



error_reporting(E_ALL);
class NS_SearchForm {
  function control(){
    echo 'I am a control panel';
  }
  function widget($args){
    $snippet = fopen("search_form_snippet.html", "r");
    echo $args['before_widget'];
    echo $args['before_title'] . 'Neahttadigisánit' . $args['after_title'];
    echo $snippet;
    echo $args['after_widget'];
  }
  function register(){
    register_sidebar_widget('Neahttadigisánit', array('Widget_name', 'widget'));
    register_widget_control('Neahttadigisánit', array('Widget_name', 'control'));
  }
}

function vn_init() {
    add_action("widgets_init", array('Widget_name', 'register'));

    // Only load plugin on non-admin pages.
    if (!is_admin()) {
        // NOTE: this is how to restrict only to admins.
        // if (current_user_can( 'manage_options' )) { }
        load_dict_css();
        load_dict_scripts();
    }
}

add_action('init', 'vn_init');

?>
