/*
 * Copyright (C) 2009 Ulteo SAS
 * http://www.ulteo.com
 * Author Julien LANGLOIS <julien@ulteo.com> 2009
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
 */


package org.ulteo.applet;

import java.awt.event.FocusEvent;
import java.awt.event.FocusListener;


public class PortalApplication extends Standalone implements FocusListener {
	public void start() {
		super.start();
		if (this.stopped || ! this.continue2run)
			return;
		this.addFocusListener(this);
		this.vnc.vc.addFocusListener(this);
	}
	
	public void focusGained(FocusEvent e) {
		System.out.println("Portal app focus gained");
		this.dialog.forwardFocusInfo(true);
	}
    
	public void focusLost(FocusEvent e) {
		System.out.println("Portal app focus lost");
		this.dialog.forwardFocusInfo(false);
	}
}
