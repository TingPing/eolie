# Copyright (c) 2017 Cedric Bellegarde <cedric.bellegarde@adishatz.org>
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

from gi.repository import Gtk, GLib, Gdk

from eolie.view import View
from eolie.popover_webview import WebViewPopover
from eolie.pages_manager import PagesManager
from eolie.sites_manager import SitesManager
from eolie.define import El


class Container(Gtk.Overlay):
    """
        Main Eolie view
    """

    def __init__(self, window):
        """
            Ini.container
            @param window as Window
        """
        Gtk.Overlay.__init__(self)
        self.__window = window
        self.__popover = WebViewPopover(window)
        self.__current = None

        self.__stack = Gtk.Stack()
        self.__stack.set_hexpand(True)
        self.__stack.set_vexpand(True)
        self.__stack.set_transition_type(Gtk.StackTransitionType.CROSSFADE)
        self.__stack.set_transition_duration(150)
        self.__stack.show()

        self.__expose_stack = Gtk.Stack()
        self.__expose_stack.set_hexpand(True)
        self.__expose_stack.set_vexpand(True)
        self.__expose_stack.set_transition_type(
                                       Gtk.StackTransitionType.OVER_RIGHT_LEFT)
        self.__expose_stack.set_transition_duration(150)
        self.__expose_stack.show()
        self.__pages_manager = PagesManager(self.__window)
        self.__pages_manager.show()
        self.__sites_manager = SitesManager(self.__window)
        if El().settings.get_value("show-sidebar"):
            self.__sites_manager.show()
        El().settings.connect("changed::show-sidebar",
                              self.__on_show_sidebar_changed)
        paned = Gtk.Paned.new(Gtk.Orientation.HORIZONTAL)
        paned.pack1(self.__sites_manager, False, False)
        paned.add2(self.__stack)
        position = El().settings.get_value("sidebar-position").get_int32()
        paned.set_position(position)
        paned.connect("notify::position", self.__on_paned_notify_position)
        paned.show()
        self.__expose_stack.add_named(paned, "stack")
        self.__expose_stack.add_named(self.__pages_manager, "expose")
        self.add(self.__expose_stack)

    def add_webview(self, uri, window_type, ephemeral=False,
                    state=None, load=True, gtime=None):
        """
            Add a web view to container
            @param uri as str
            @param window_type as Gdk.WindowType
            @param ephemeral as bool
            @param state as WebViewSessionState
            @param load as bool
            @param gtime as int
            @return NEVER RETURN SOMETHING HERE #258
        """
        webview = View.get_new_webview(ephemeral, self.__window)
        if gtime is not None:
            # We force atime to be sure child is initially sorted after parent
            webview.set_atime(gtime)
            webview.set_gtime(gtime)
        if state is not None:
            webview.restore_session_state(state)
        self.add_view(webview, window_type)
        if uri is not None:
            if load:
                # Do not load uri until we are on screen
                GLib.idle_add(webview.load_uri, uri)
            else:
                webview.set_delayed_uri(uri)

    def add_view(self, webview, window_type):
        """
            Add view to container
            @param webview as WebView
            @param window_type as Gdk.WindowType
        """
        view = self.__get_new_view(webview)
        view.show()
        self.__pages_manager.add_child(view)
        # Force window type as current window is not visible
        if self.__expose_stack.get_visible_child_name() == "expose":
            window_type = Gdk.WindowType.OFFSCREEN
        if window_type == Gdk.WindowType.CHILD:
            self.__current = view
            self.__stack.add(view)
            self.__pages_manager.update_visible_child()
            self.__sites_manager.update_visible_child()
            self.__stack.set_visible_child(view)
        elif window_type == Gdk.WindowType.OFFSCREEN:
            # Little hack, we force webview to be shown (offscreen)
            # This allow getting snapshots from webkit
            window = Gtk.OffscreenWindow.new()
            view.set_size_request(self.get_allocated_width(),
                                  self.get_allocated_height())
            window.add(view)
            window.show()
            window.remove(view)
            view.set_size_request(-1, -1)
            self.__stack.add(view)
            window.destroy()
        # Do not count container views as destroy may be pending on somes
        # Reason: we do not remove/destroy view to let stack animation run
        count = str(len(self.__pages_manager.children))
        self.__window.toolbar.actions.count_label.set_text(count)

    def load_uri(self, uri):
        """
            Load uri in current view
            @param uri as str
        """
        if self.current is not None:
            self.current.webview.load_uri(uri)

    def set_current(self, view, switch=False):
        """
            Set visible view
            @param view as View
            @param switch as bool
        """
        self.__current = view
        self.__pages_manager.update_visible_child()
        self.__sites_manager.update_visible_child()
        if switch:
            self.__stack.set_visible_child(view)

    def popup_webview(self, webview, destroy):
        """
            Show webview in popopver
            @param webview as WebView
            @param destroy webview when popover hidden
        """
        view = View(webview, self.__window)
        view.show()
        self.__popover.add_view(view, destroy)
        if not self.__popover.is_visible():
            self.__popover.set_size_request(
                                 self.__window.get_allocated_width() / 3,
                                 self.__window.get_allocated_height() / 1.5)
            self.__popover.set_relative_to(self.__window.toolbar)
            self.__popover.set_position(Gtk.PositionType.BOTTOM)
            self.__popover.popup()

    def set_expose(self, expose, search=False):
        """
            Show current views
            @param expose as bool
            @param search as bool
        """
        # Show search bar
        child = self.__expose_stack.get_child_by_name("expose")
        if not child.filtered:
            GLib.timeout_add(500, child.set_filtered, search and expose)
        # Show expose mode
        if expose:
            self.__pages_manager.update_sort()
            self.__expose_stack.set_visible_child_name("expose")
        else:
            if self.__stack.get_visible_child() != self.__current:
                self.__stack.set_visible_child(self.__current)
            self.__expose_stack.set_visible_child_name("stack")
            self.__window.toolbar.actions.view_button.set_active(False)
            self.__window.container.pages_manager.set_filter("")
            child.set_filtered(False)

    @property
    def pages_manager(self):
        """
            Get pages manager
            @return PagesManager
        """
        return self.__pages_manager

    @property
    def sites_manager(self):
        """
            Get sites manager
            @return SitesManager
        """
        return self.__sites_manager

    @property
    def views(self):
        """
            Get views
            @return views as [View]
        """
        return self.__stack.get_children()

    @property
    def current(self):
        """
            Current view
            @return WebView
        """
        return self.__current

#######################
# PRIVATE             #
#######################
    def __get_new_view(self, webview):
        """
            Get a new view
            @param webview as WebView
            @return View
        """
        view = View(webview, self.__window)
        view.show()
        return view

    def __on_paned_notify_position(self, paned, ignore):
        """
            Update SitesManager width based on current position
            @param paned as Gtk.Paned
            @param ignore as GParamInt
        """
        position = paned.get_position()
        El().settings.set_value("sidebar-position",
                                GLib.Variant("i", position))
        self.__sites_manager.set_minimal(position < 80)

    def __on_show_sidebar_changed(self, settings, value):
        """
            Show/hide panel
            @param settings as Gio.Settings
            @param value as bool
        """
        if El().settings.get_value("show-sidebar"):
            self.__sites_manager.show()
        else:
            self.__sites_manager.hide()
