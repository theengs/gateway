(window.webpackJsonp=window.webpackJsonp||[]).push([[10],{410:function(a,e,t){"use strict";t.r(e);var s=t(56),n=Object(s.a)({},(function(){var a=this,e=a.$createElement,t=a._self._c||e;return t("ContentSlotsDistributor",{attrs:{"slot-key":a.$parent.slotKey}},[t("h1",{attrs:{id:"install"}},[t("a",{staticClass:"header-anchor",attrs:{href:"#install"}},[a._v("#")]),a._v(" Install")]),a._v(" "),t("p",[a._v("Several methods are available to install the gateway:")]),a._v(" "),t("h2",{attrs:{id:"install-theengs-gateway-as-a-pip-package"}},[t("a",{staticClass:"header-anchor",attrs:{href:"#install-theengs-gateway-as-a-pip-package"}},[a._v("#")]),a._v(" Install Theengs Gateway as a pip package")]),a._v(" "),t("p",[a._v("Prerequisites:")]),a._v(" "),t("ul",[t("li",[a._v("Install "),t("a",{attrs:{href:"https://www.python.org/downloads/",target:"_blank",rel:"noopener noreferrer"}},[a._v("Python3"),t("OutboundLink")],1)]),a._v(" "),t("li",[a._v("Install "),t("a",{attrs:{href:"https://pip.pypa.io/en/stable/installation/",target:"_blank",rel:"noopener noreferrer"}},[a._v("pip"),t("OutboundLink")],1)])]),a._v(" "),t("p",[a._v("Make sure to have the latest version of pip if it's already installed:")]),a._v(" "),t("div",{staticClass:"language-shell line-numbers-mode"},[t("pre",{pre:!0,attrs:{class:"language-shell"}},[t("code",[a._v("pip "),t("span",{pre:!0,attrs:{class:"token function"}},[a._v("install")]),a._v(" --upgrade pip\n")])]),a._v(" "),t("div",{staticClass:"line-numbers-wrapper"},[t("span",{staticClass:"line-number"},[a._v("1")]),t("br")])]),t("p",[a._v("Then install Theengs Gateway with:")]),a._v(" "),t("div",{staticClass:"language-shell line-numbers-mode"},[t("pre",{pre:!0,attrs:{class:"language-shell"}},[t("code",[a._v("pip "),t("span",{pre:!0,attrs:{class:"token function"}},[a._v("install")]),a._v(" TheengsGateway\n")])]),a._v(" "),t("div",{staticClass:"line-numbers-wrapper"},[t("span",{staticClass:"line-number"},[a._v("1")]),t("br")])]),t("p",[a._v("You can access advanced configuration by typing:")]),a._v(" "),t("div",{staticClass:"language-shell line-numbers-mode"},[t("pre",{pre:!0,attrs:{class:"language-shell"}},[t("code",[a._v("python3 -m TheengsGateway -h\n")])]),a._v(" "),t("div",{staticClass:"line-numbers-wrapper"},[t("span",{staticClass:"line-number"},[a._v("1")]),t("br")])]),t("h2",{attrs:{id:"install-theengs-gateway-as-an-add-on-in-home-assistant"}},[t("a",{staticClass:"header-anchor",attrs:{href:"#install-theengs-gateway-as-an-add-on-in-home-assistant"}},[a._v("#")]),a._v(" Install Theengs Gateway as an Add ON in Home Assistant")]),a._v(" "),t("ol",[t("li",[a._v("Add the Add-on repository into the add-on store")])]),a._v(" "),t("p",[t("a",{attrs:{href:"https://my.home-assistant.io/redirect/supervisor_add_addon_repository/?repository_url=https%3A%2F%2Fgithub.com%2Fmihsu81%2Faddon-theengsgw",target:"_blank",rel:"noopener noreferrer"}},[t("img",{attrs:{src:"https://my.home-assistant.io/badges/supervisor_add_addon_repository.svg",alt:"Open your Home Assistant instance and show the add add-on repository dialog with a specific repository URL pre-filled."}}),t("OutboundLink")],1)]),a._v(" "),t("p",[a._v("Or by going to Settings -> Add-ons -> Add-on store -> ⁞ (Menu) -> Repositories -> Fill in the URL "),t("code",[a._v("https://github.com/mihsu81/addon-theengsgw")]),a._v(" -> Add.")]),a._v(" "),t("ol",{attrs:{start:"2"}},[t("li",[a._v("You should now see "),t("strong",[a._v("TheengsGateway HA Add-on")]),a._v(" at the bottom list.")]),a._v(" "),t("li",[a._v("Click on "),t("strong",[a._v("TheengsGateway")]),a._v(", then click "),t("strong",[a._v("Install")]),a._v(".")]),a._v(" "),t("li",[a._v("Under the "),t("strong",[a._v("Configuration")]),a._v(" tab, change the settings appropriately (at least MQTT parameters), see "),t("a",{attrs:{href:"https://github.com/mihsu81/addon-theengsgw/blob/main/theengsgateway/DOCS.md#parameters",target:"_blank",rel:"noopener noreferrer"}},[a._v("Parameters"),t("OutboundLink")],1),a._v(".")]),a._v(" "),t("li",[a._v("Start the Add-on.")])]),a._v(" "),t("h2",{attrs:{id:"install-theengs-gateway-as-a-snap"}},[t("a",{staticClass:"header-anchor",attrs:{href:"#install-theengs-gateway-as-a-snap"}},[a._v("#")]),a._v(" Install Theengs Gateway as a snap")]),a._v(" "),t("p",[a._v("Theengs Gateway is also packaged as a snap in the "),t("a",{attrs:{href:"https://snapcraft.io/theengs-gateway",target:"_blank",rel:"noopener noreferrer"}},[a._v("Snap Store"),t("OutboundLink")],1),a._v(". If you have "),t("code",[a._v("snapd")]),a._v(" running on your Linux distribution, which is the case by default on Ubuntu, you can install the Theengs Gateway snap as:")]),a._v(" "),t("p",[t("a",{attrs:{href:"https://snapcraft.io/theengs-gateway",target:"_blank",rel:"noopener noreferrer"}},[t("img",{attrs:{src:"https://snapcraft.io/static/images/badges/en/snap-store-white.svg",alt:"Get it from the Snap Store"}}),t("OutboundLink")],1)]),a._v(" "),t("div",{staticClass:"language-shell line-numbers-mode"},[t("pre",{pre:!0,attrs:{class:"language-shell"}},[t("code",[a._v("snap "),t("span",{pre:!0,attrs:{class:"token function"}},[a._v("install")]),a._v(" theengs-gateway\n")])]),a._v(" "),t("div",{staticClass:"line-numbers-wrapper"},[t("span",{staticClass:"line-number"},[a._v("1")]),t("br")])]),t("p",[a._v("Have a look at the "),t("a",{attrs:{href:"https://github.com/theengs/gateway-snap",target:"_blank",rel:"noopener noreferrer"}},[a._v("Theengs Gateway Snap"),t("OutboundLink")],1),a._v(" documentation for more information about how to configure and start Theengs Gateway as a service.")]),a._v(" "),t("h2",{attrs:{id:"install-theengs-gateway-as-a-docker"}},[t("a",{staticClass:"header-anchor",attrs:{href:"#install-theengs-gateway-as-a-docker"}},[a._v("#")]),a._v(" Install Theengs Gateway as a docker")]),a._v(" "),t("p",[a._v("Theengs Gateway is also available from docker hub thanks to "),t("a",{attrs:{href:"https://github.com/maretodoric",target:"_blank",rel:"noopener noreferrer"}},[a._v("@maretodoric"),t("OutboundLink")],1)]),a._v(" "),t("img",{attrs:{alt:"Docker Image Size (latest by date)",src:"https://img.shields.io/docker/image-size/theengs/gateway"}}),a._v(" "),t("div",{staticClass:"language-shell line-numbers-mode"},[t("pre",{pre:!0,attrs:{class:"language-shell"}},[t("code",[t("span",{pre:!0,attrs:{class:"token function"}},[a._v("docker")]),a._v(" pull theengs/gateway\n")])]),a._v(" "),t("div",{staticClass:"line-numbers-wrapper"},[t("span",{staticClass:"line-number"},[a._v("1")]),t("br")])]),t("h2",{attrs:{id:"advanced-users-build-and-install"}},[t("a",{staticClass:"header-anchor",attrs:{href:"#advanced-users-build-and-install"}},[a._v("#")]),a._v(" Advanced users - Build and install")]),a._v(" "),t("p",[a._v("Make sure to have the latest version of pip:")]),a._v(" "),t("div",{staticClass:"language-shell line-numbers-mode"},[t("pre",{pre:!0,attrs:{class:"language-shell"}},[t("code",[a._v("pip "),t("span",{pre:!0,attrs:{class:"token function"}},[a._v("install")]),a._v(" --upgrade pip\n")])]),a._v(" "),t("div",{staticClass:"line-numbers-wrapper"},[t("span",{staticClass:"line-number"},[a._v("1")]),t("br")])]),t("p",[a._v("Then clone the repository:")]),a._v(" "),t("div",{staticClass:"language- line-numbers-mode"},[t("pre",{pre:!0,attrs:{class:"language-text"}},[t("code",[a._v("git clone https://github.com/theengs/gateway.git\ncd gateway\n")])]),a._v(" "),t("div",{staticClass:"line-numbers-wrapper"},[t("span",{staticClass:"line-number"},[a._v("1")]),t("br"),t("span",{staticClass:"line-number"},[a._v("2")]),t("br")])]),t("p",[a._v("Then build and install the package:")]),a._v(" "),t("div",{staticClass:"language- line-numbers-mode"},[t("pre",{pre:!0,attrs:{class:"language-text"}},[t("code",[a._v("pip install .\n")])]),a._v(" "),t("div",{staticClass:"line-numbers-wrapper"},[t("span",{staticClass:"line-number"},[a._v("1")]),t("br")])]),t("div",{staticClass:"custom-block tip"},[t("p",{staticClass:"custom-block-title"},[a._v("TIP")]),a._v(" "),t("p",[a._v("When launching the gateway you must be outside of its source code folder to avoid errors")])])])}),[],!1,null,null,null);e.default=n.exports}}]);