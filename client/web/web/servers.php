<?php
/**
 * Copyright (C) 2010 Ulteo SAS
 * http://www.ulteo.com
 * Author Jeremy DESVAGES <jeremy@ulteo.com>
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

require_once(dirname(__FILE__).'/includes/core.inc.php');

function return_error($errno_, $errstr_) {
	$dom = new DomDocument('1.0', 'utf-8');
	$node = $dom->createElement('error');
	$node->setAttribute('id', $errno_);
	$node->setAttribute('message', $errstr_);
	$dom->appendChild($node);
	return $dom->saveXML();
}

header('Content-Type: text/xml; charset=utf-8');

$dom = new DomDocument('1.0', 'utf-8');
$buf = @$dom->loadXML($_SESSION['xml']);
if (! $buf) {
	echo return_error(0, 'Invalid XML');
	die();
}

if (! $dom->hasChildNodes()) {
	echo return_error(0, 'Invalid XML');
	die();
}

$server_nodes = $dom->getElementsByTagName('server');
foreach ($server_nodes as $server_node) {
	if (array_key_exists('gateway', $_SESSION) && $_SESSION['gateway'] === true)
		$server_node->setAttribute('fqdn', $_SESSION['ovd-client']['server']);
}

$xml = $dom->saveXML();

echo $xml;
die();
