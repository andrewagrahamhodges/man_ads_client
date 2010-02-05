<?php
/**
 * Copyright (C) 2009-2010 Ulteo SAS
 * http://www.ulteo.com
 * Author Julien LANGLOIS <julien@ulteo.com>
 * Author Laurent CLOUET <laurent@ulteo.com>
 *
 * This program is free software; you can redistribute it and/or
 * modify it under the terms of the GNU General Public License
 * as published by the Free Software Foundation; version 2
 * of the License.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program; if not, write to the Free Software
 * Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
 **/
require_once(dirname(__FILE__).'/../includes/core.inc.php');

class Configuration_mode_internal extends Configuration_mode {

  public function getPrettyName() {
    return _('Internal');
  }

  public function careAbout($userDB) {
    return in_array($userDB, array('sql'));
  }

  public function has_change($oldprefs, $newprefs) {
    $old = $oldprefs->get('UserDB', 'enable');
    $new = $newprefs->get('UserDB', 'enable');

    return array($old==$new, False);
  }

  public function form_valid($form) {
	if (! in_array($form['homedir'], array('local', 'dav')))
		return False;

    return True;
  }

  public function form_read($form, $prefs) {
    // Select Module as UserDB
    $prefs->set('UserDB', 'enable', 'sql');


    // Select Module for UserGroupDB
    $prefs->set('UserGroupDB', 'enable', 'sql');


    // Set the FS type
	$prefs->set('plugins', 'FS', $form['homedir']);

    return True;
  }


  public function config2form($prefs) {
    $form = array();
    $config = $prefs->get('UserDB', 'enable');

	$form['homedir']  = $prefs->get('plugins', 'FS');
    return $form;
  }

  public function display($form) {
    $str= '<h1>'._('Internal Database Profiles').'</h1>';

    $str.= '<div class="section">';
    $str.= _('This is the default Profile manager. This profile manager saves all the data into a the same SQL database as you defined it in the system configuration.');
    $str.= '</div>';

	$str.= '<div class="section">';
	$str.= '<h3>'._('Home Directory').'</h3>';
	$str.= '<input class="input_radio" type="radio" name="homedir" value="local"';
	if ($form['homedir'] == 'local')
		$str.= ' checked="checked"';
	$str.= '/>';
	$str.= _('Use Internal home directory (no server replication)');
	$str.= '<br/>';

	$str.= '<input class="input_radio" type="radio" name="homedir" value="dav" ';
	if ($form['homedir'] == 'dav')
		$str.= ' checked="checked"';
	$str.= '/>';
	$str.= _('Use shared folders');
	$str.= '<br/>';
	$str.= '</div>';

    return $str;
  }

  public function display_sumup($prefs) {
    $config = $prefs->get('UserDB', 'enable');

    $str = '';
    if ($config == 'sql')
      $str.= _('Use a dynamic internal user list');

    return $str;
  }

}
