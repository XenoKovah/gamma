!function($){$(function(){$.support.transition=function(){var transitionEnd=function(){var el=document.createElement("bootstrap"),transEndEventNames={"WebkitTransition":"webkitTransitionEnd","MozTransition":"transitionend","OTransition":"oTransitionEnd otransitionend","transition":"transitionend"},name;for(name in transEndEventNames)if(el.style[name]!==undefined)return transEndEventNames[name]}();return transitionEnd&&{end:transitionEnd}}()})}(window.jQuery);
!function($){var Modal=function(element,options){this.options=options;this.$element=$(element).delegate('[data-dismiss="modal"]',"click.dismiss.modal",$.proxy(this.hide,this));this.options.remote&&this.$element.find(".modal-body").load(this.options.remote)};Modal.prototype={constructor:Modal,toggle:function(){return this[!this.isShown?"show":"hide"]()},show:function(){var that=this,e=$.Event("show");this.$element.trigger(e);if(this.isShown||e.isDefaultPrevented())return;this.isShown=true;this.escape();
this.backdrop(function(){var transition=$.support.transition&&that.$element.hasClass("fade");if(!that.$element.parent().length)that.$element.appendTo(document.body);that.$element.show();if(transition)that.$element[0].offsetWidth;that.$element.addClass("in").attr("aria-hidden",false);that.enforceFocus();transition?that.$element.one($.support.transition.end,function(){that.$element.focus().trigger("shown")}):that.$element.focus().trigger("shown")})},hide:function(e){e&&e.preventDefault();var that=this;
e=$.Event("hide");this.$element.trigger(e);if(!this.isShown||e.isDefaultPrevented())return;this.isShown=false;this.escape();$(document).off("focusin.modal");this.$element.removeClass("in").attr("aria-hidden",true);$.support.transition&&this.$element.hasClass("fade")?this.hideWithTransition():this.hideModal()},enforceFocus:function(){var that=this;$(document).on("focusin.modal",function(e){if(that.$element[0]!==e.target&&!that.$element.has(e.target).length)that.$element.focus()})},escape:function(){var that=
this;if(this.isShown&&this.options.keyboard)this.$element.on("keyup.dismiss.modal",function(e){e.which==27&&that.hide()});else if(!this.isShown)this.$element.off("keyup.dismiss.modal")},hideWithTransition:function(){var that=this,timeout=setTimeout(function(){that.$element.off($.support.transition.end);that.hideModal()},500);this.$element.one($.support.transition.end,function(){clearTimeout(timeout);that.hideModal()})},hideModal:function(){var that=this;this.$element.hide();this.backdrop(function(){that.removeBackdrop();
that.$element.trigger("hidden")})},removeBackdrop:function(){this.$backdrop&&this.$backdrop.remove();this.$backdrop=null},backdrop:function(callback){var that=this,animate=this.$element.hasClass("fade")?"fade":"";if(this.isShown&&this.options.backdrop){var doAnimate=$.support.transition&&animate;this.$backdrop=$('<div class="modal-backdrop '+animate+'" />').appendTo(document.body);this.$backdrop.click(this.options.backdrop=="static"?$.proxy(this.$element[0].focus,this.$element[0]):$.proxy(this.hide,
this));if(doAnimate)this.$backdrop[0].offsetWidth;this.$backdrop.addClass("in");if(!callback)return;doAnimate?this.$backdrop.one($.support.transition.end,callback):callback()}else if(!this.isShown&&this.$backdrop){this.$backdrop.removeClass("in");$.support.transition&&this.$element.hasClass("fade")?this.$backdrop.one($.support.transition.end,callback):callback()}else if(callback)callback()}};var old=$.fn.modal;$.fn.modal=function(option){return this.each(function(){var $this=$(this),data=$this.data("modal"),
options=$.extend({},$.fn.modal.defaults,$this.data(),typeof option=="object"&&option);if(!data)$this.data("modal",data=new Modal(this,options));if(typeof option=="string")data[option]();else if(options.show)data.show()})};$.fn.modal.defaults={backdrop:true,keyboard:true,show:true};$.fn.modal.Constructor=Modal;$.fn.modal.noConflict=function(){$.fn.modal=old;return this};$(document).on("click.modal.data-api",'[data-toggle="modal"]',function(e){var $this=$(this),href=$this.attr("href"),$target=$($this.attr("data-target")||
href&&href.replace(/.*(?=#[^\s]+$)/,"")),option=$target.data("modal")?"toggle":$.extend({remote:!/#/.test(href)&&href},$target.data(),$this.data());e.preventDefault();$target.modal(option).one("hide",function(){$this.focus()})})}(window.jQuery);
!function($){var toggle="[data-toggle=dropdown]",Dropdown=function(element){var $el=$(element).on("click.dropdown.data-api",this.toggle);$("html").on("click.dropdown.data-api",function(){$el.parent().removeClass("open")})};Dropdown.prototype={constructor:Dropdown,toggle:function(e){var $this=$(this),$parent,isActive;if($this.is(".disabled, :disabled"))return;$parent=getParent($this);isActive=$parent.hasClass("open");clearMenus();if(!isActive){if("ontouchstart"in document.documentElement)$('<div class="dropdown-backdrop"/>').insertBefore($(this)).on("click",
clearMenus);$parent.toggleClass("open")}$this.focus();return false},keydown:function(e){var $this,$items,$active,$parent,isActive,index;if(!/(38|40|27)/.test(e.keyCode))return;$this=$(this);e.preventDefault();e.stopPropagation();if($this.is(".disabled, :disabled"))return;$parent=getParent($this);isActive=$parent.hasClass("open");if(!isActive||isActive&&e.keyCode==27){if(e.which==27)$parent.find(toggle).focus();return $this.click()}$items=$("[role=menu] li:not(.divider):visible a",$parent);if(!$items.length)return;
index=$items.index($items.filter(":focus"));if(e.keyCode==38&&index>0)index--;if(e.keyCode==40&&index<$items.length-1)index++;if(!~index)index=0;$items.eq(index).focus()}};function clearMenus(){$(".dropdown-backdrop").remove();$(toggle).each(function(){getParent($(this)).removeClass("open")})}function getParent($this){var selector=$this.attr("data-target"),$parent;if(!selector){selector=$this.attr("href");selector=selector&&/#/.test(selector)&&selector.replace(/.*(?=#[^\s]*$)/,"")}$parent=selector&&
$(selector);if(!$parent||!$parent.length)$parent=$this.parent();return $parent}var old=$.fn.dropdown;$.fn.dropdown=function(option){return this.each(function(){var $this=$(this),data=$this.data("dropdown");if(!data)$this.data("dropdown",data=new Dropdown(this));if(typeof option=="string")data[option].call($this)})};$.fn.dropdown.Constructor=Dropdown;$.fn.dropdown.noConflict=function(){$.fn.dropdown=old;return this};$(document).on("click.dropdown.data-api",clearMenus).on("click.dropdown.data-api",
".dropdown form",function(e){e.stopPropagation()}).on("click.dropdown.data-api",toggle,Dropdown.prototype.toggle).on("keydown.dropdown.data-api",toggle+", [role=menu]",Dropdown.prototype.keydown)}(window.jQuery);
!function($){function ScrollSpy(element,options){var process=$.proxy(this.process,this),$element=$(element).is("body")?$(window):$(element),href;this.options=$.extend({},$.fn.scrollspy.defaults,options);this.$scrollElement=$element.on("scroll.scroll-spy.data-api",process);this.selector=(this.options.target||(href=$(element).attr("href"))&&href.replace(/.*(?=#[^\s]+$)/,"")||"")+" .nav li > a";this.$body=$("body");this.refresh();this.process()}ScrollSpy.prototype={constructor:ScrollSpy,refresh:function(){var self=
this,$targets;this.offsets=$([]);this.targets=$([]);$targets=this.$body.find(this.selector).map(function(){var $el=$(this),href=$el.data("target")||$el.attr("href"),$href=/^#\w/.test(href)&&$(href);return $href&&$href.length&&[[$href.position().top+(!$.isWindow(self.$scrollElement.get(0))&&self.$scrollElement.scrollTop()),href]]||null}).sort(function(a,b){return a[0]-b[0]}).each(function(){self.offsets.push(this[0]);self.targets.push(this[1])})},process:function(){var scrollTop=this.$scrollElement.scrollTop()+
this.options.offset,scrollHeight=this.$scrollElement[0].scrollHeight||this.$body[0].scrollHeight,maxScroll=scrollHeight-this.$scrollElement.height(),offsets=this.offsets,targets=this.targets,activeTarget=this.activeTarget,i;if(scrollTop>=maxScroll)return activeTarget!=(i=targets.last()[0])&&this.activate(i);for(i=offsets.length;i--;)activeTarget!=targets[i]&&scrollTop>=offsets[i]&&(!offsets[i+1]||scrollTop<=offsets[i+1])&&this.activate(targets[i])},activate:function(target){var active,selector;this.activeTarget=
target;$(this.selector).parent(".active").removeClass("active");selector=this.selector+'[data-target="'+target+'"],'+this.selector+'[href="'+target+'"]';active=$(selector).parent("li").addClass("active");if(active.parent(".dropdown-menu").length)active=active.closest("li.dropdown").addClass("active");active.trigger("activate")}};var old=$.fn.scrollspy;$.fn.scrollspy=function(option){return this.each(function(){var $this=$(this),data=$this.data("scrollspy"),options=typeof option=="object"&&option;
if(!data)$this.data("scrollspy",data=new ScrollSpy(this,options));if(typeof option=="string")data[option]()})};$.fn.scrollspy.Constructor=ScrollSpy;$.fn.scrollspy.defaults={offset:10};$.fn.scrollspy.noConflict=function(){$.fn.scrollspy=old;return this};$(window).on("load",function(){$('[data-spy="scroll"]').each(function(){var $spy=$(this);$spy.scrollspy($spy.data())})})}(window.jQuery);
!function($){var Tab=function(element){this.element=$(element)};Tab.prototype={constructor:Tab,show:function(){var $this=this.element,$ul=$this.closest("ul:not(.dropdown-menu)"),selector=$this.attr("data-target"),previous,$target,e;if(!selector){selector=$this.attr("href");selector=selector&&selector.replace(/.*(?=#[^\s]*$)/,"")}if($this.parent("li").hasClass("active"))return;previous=$ul.find(".active:last a")[0];e=$.Event("show",{relatedTarget:previous});$this.trigger(e);if(e.isDefaultPrevented())return;
$target=$(selector);this.activate($this.parent("li"),$ul);this.activate($target,$target.parent(),function(){$this.trigger({type:"shown",relatedTarget:previous})})},activate:function(element,container,callback){var $active=container.find("> .active"),transition=callback&&$.support.transition&&$active.hasClass("fade");function next(){$active.removeClass("active").find("> .dropdown-menu > .active").removeClass("active");element.addClass("active");if(transition){element[0].offsetWidth;element.addClass("in")}else element.removeClass("fade");
if(element.parent(".dropdown-menu"))element.closest("li.dropdown").addClass("active");callback&&callback()}transition?$active.one($.support.transition.end,next):next();$active.removeClass("in")}};var old=$.fn.tab;$.fn.tab=function(option){return this.each(function(){var $this=$(this),data=$this.data("tab");if(!data)$this.data("tab",data=new Tab(this));if(typeof option=="string")data[option]()})};$.fn.tab.Constructor=Tab;$.fn.tab.noConflict=function(){$.fn.tab=old;return this};$(document).on("click.tab.data-api",
'[data-toggle="tab"], [data-toggle="pill"]',function(e){e.preventDefault();$(this).tab("show")})}(window.jQuery);
!function($){var Tooltip=function(element,options){this.init("tooltip",element,options)};Tooltip.prototype={constructor:Tooltip,init:function(type,element,options){var eventIn,eventOut,triggers,trigger,i;this.type=type;this.$element=$(element);this.options=this.getOptions(options);this.enabled=true;triggers=this.options.trigger.split(" ");for(i=triggers.length;i--;){trigger=triggers[i];if(trigger=="click")this.$element.on("click."+this.type,this.options.selector,$.proxy(this.toggle,this));else if(trigger!=
"manual"){eventIn=trigger=="hover"?"mouseenter":"focus";eventOut=trigger=="hover"?"mouseleave":"blur";this.$element.on(eventIn+"."+this.type,this.options.selector,$.proxy(this.enter,this));this.$element.on(eventOut+"."+this.type,this.options.selector,$.proxy(this.leave,this))}}this.options.selector?this._options=$.extend({},this.options,{trigger:"manual",selector:""}):this.fixTitle()},getOptions:function(options){options=$.extend({},$.fn[this.type].defaults,this.$element.data(),options);if(options.delay&&
typeof options.delay=="number")options.delay={show:options.delay,hide:options.delay};return options},enter:function(e){var defaults=$.fn[this.type].defaults,options={},self;this._options&&$.each(this._options,function(key,value){if(defaults[key]!=value)options[key]=value},this);self=$(e.currentTarget)[this.type](options).data(this.type);if(!self.options.delay||!self.options.delay.show)return self.show();clearTimeout(this.timeout);self.hoverState="in";this.timeout=setTimeout(function(){if(self.hoverState==
"in")self.show()},self.options.delay.show)},leave:function(e){var self=$(e.currentTarget)[this.type](this._options).data(this.type);if(this.timeout)clearTimeout(this.timeout);if(!self.options.delay||!self.options.delay.hide)return self.hide();self.hoverState="out";this.timeout=setTimeout(function(){if(self.hoverState=="out")self.hide()},self.options.delay.hide)},show:function(){var $tip,pos,actualWidth,actualHeight,placement,tp,e=$.Event("show");if(this.hasContent()&&this.enabled){this.$element.trigger(e);
if(e.isDefaultPrevented())return;$tip=this.tip();this.setContent();if(this.options.animation)$tip.addClass("fade");placement=typeof this.options.placement=="function"?this.options.placement.call(this,$tip[0],this.$element[0]):this.options.placement;$tip.detach().css({top:0,left:0,display:"block"});this.options.container?$tip.appendTo(this.options.container):$tip.insertAfter(this.$element);pos=this.getPosition();actualWidth=$tip[0].offsetWidth;actualHeight=$tip[0].offsetHeight;switch(placement){case "bottom":tp=
{top:pos.top+pos.height,left:pos.left+pos.width/2-actualWidth/2};break;case "top":tp={top:pos.top-actualHeight,left:pos.left+pos.width/2-actualWidth/2};break;case "left":tp={top:pos.top+pos.height/2-actualHeight/2,left:pos.left-actualWidth};break;case "right":tp={top:pos.top+pos.height/2-actualHeight/2,left:pos.left+pos.width};break}this.applyPlacement(tp,placement);this.$element.trigger("shown")}},applyPlacement:function(offset,placement){var $tip=this.tip(),width=$tip[0].offsetWidth,height=$tip[0].offsetHeight,
actualWidth,actualHeight,delta,replace;$tip.offset(offset).addClass(placement).addClass("in");actualWidth=$tip[0].offsetWidth;actualHeight=$tip[0].offsetHeight;if(placement=="top"&&actualHeight!=height){offset.top=offset.top+height-actualHeight;replace=true}if(placement=="bottom"||placement=="top"){delta=0;if(offset.left<0){delta=offset.left*-2;offset.left=0;$tip.offset(offset);actualWidth=$tip[0].offsetWidth;actualHeight=$tip[0].offsetHeight}this.replaceArrow(delta-width+actualWidth,actualWidth,
"left")}else this.replaceArrow(actualHeight-height,actualHeight,"top");if(replace)$tip.offset(offset)},replaceArrow:function(delta,dimension,position){this.arrow().css(position,delta?50*(1-delta/dimension)+"%":"")},setContent:function(){var $tip=this.tip(),title=this.getTitle();$tip.find(".tooltip-inner")[this.options.html?"html":"text"](title);$tip.removeClass("fade in top bottom left right")},hide:function(){var that=this,$tip=this.tip(),e=$.Event("hide");this.$element.trigger(e);if(e.isDefaultPrevented())return;
$tip.removeClass("in");function removeWithAnimation(){var timeout=setTimeout(function(){$tip.off($.support.transition.end).detach()},500);$tip.one($.support.transition.end,function(){clearTimeout(timeout);$tip.detach()})}$.support.transition&&this.$tip.hasClass("fade")?removeWithAnimation():$tip.detach();this.$element.trigger("hidden");return this},fixTitle:function(){var $e=this.$element;if($e.attr("title")||typeof $e.attr("data-original-title")!="string")$e.attr("data-original-title",$e.attr("title")||
"").attr("title","")},hasContent:function(){return this.getTitle()},getPosition:function(){var el=this.$element[0];return $.extend({},typeof el.getBoundingClientRect=="function"?el.getBoundingClientRect():{width:el.offsetWidth,height:el.offsetHeight},this.$element.offset())},getTitle:function(){var title,$e=this.$element,o=this.options;title=$e.attr("data-original-title")||(typeof o.title=="function"?o.title.call($e[0]):o.title);return title},tip:function(){return this.$tip=this.$tip||$(this.options.template)},
arrow:function(){return this.$arrow=this.$arrow||this.tip().find(".tooltip-arrow")},validate:function(){if(!this.$element[0].parentNode){this.hide();this.$element=null;this.options=null}},enable:function(){this.enabled=true},disable:function(){this.enabled=false},toggleEnabled:function(){this.enabled=!this.enabled},toggle:function(e){var self=e?$(e.currentTarget)[this.type](this._options).data(this.type):this;self.tip().hasClass("in")?self.hide():self.show()},destroy:function(){this.hide().$element.off("."+
this.type).removeData(this.type)}};var old=$.fn.tooltip;$.fn.tooltip=function(option){return this.each(function(){var $this=$(this),data=$this.data("tooltip"),options=typeof option=="object"&&option;if(!data)$this.data("tooltip",data=new Tooltip(this,options));if(typeof option=="string")data[option]()})};$.fn.tooltip.Constructor=Tooltip;$.fn.tooltip.defaults={animation:true,placement:"top",selector:false,template:'<div class="tooltip"><div class="tooltip-arrow"></div><div class="tooltip-inner"></div></div>',
trigger:"hover focus",title:"",delay:0,html:false,container:false};$.fn.tooltip.noConflict=function(){$.fn.tooltip=old;return this}}(window.jQuery);
!function($){var Popover=function(element,options){this.init("popover",element,options)};Popover.prototype=$.extend({},$.fn.tooltip.Constructor.prototype,{constructor:Popover,setContent:function(){var $tip=this.tip(),title=this.getTitle(),content=this.getContent();$tip.find(".popover-title")[this.options.html?"html":"text"](title);$tip.find(".popover-content")[this.options.html?"html":"text"](content);$tip.removeClass("fade top bottom left right in")},hasContent:function(){return this.getTitle()||
this.getContent()},getContent:function(){var content,$e=this.$element,o=this.options;content=(typeof o.content=="function"?o.content.call($e[0]):o.content)||$e.attr("data-content");return content},tip:function(){if(!this.$tip)this.$tip=$(this.options.template);return this.$tip},destroy:function(){this.hide().$element.off("."+this.type).removeData(this.type)}});var old=$.fn.popover;$.fn.popover=function(option){return this.each(function(){var $this=$(this),data=$this.data("popover"),options=typeof option==
"object"&&option;if(!data)$this.data("popover",data=new Popover(this,options));if(typeof option=="string")data[option]()})};$.fn.popover.Constructor=Popover;$.fn.popover.defaults=$.extend({},$.fn.tooltip.defaults,{placement:"right",trigger:"click",content:"",template:'<div class="popover"><div class="arrow"></div><h3 class="popover-title"></h3><div class="popover-content"></div></div>'});$.fn.popover.noConflict=function(){$.fn.popover=old;return this}}(window.jQuery);
!function($){var Affix=function(element,options){this.options=$.extend({},$.fn.affix.defaults,options);this.$window=$(window).on("scroll.affix.data-api",$.proxy(this.checkPosition,this)).on("click.affix.data-api",$.proxy(function(){setTimeout($.proxy(this.checkPosition,this),1)},this));this.$element=$(element);this.checkPosition()};Affix.prototype.checkPosition=function(){if(!this.$element.is(":visible"))return;var scrollHeight=$(document).height(),scrollTop=this.$window.scrollTop(),position=this.$element.offset(),
offset=this.options.offset,offsetBottom=offset.bottom,offsetTop=offset.top,reset="affix affix-top affix-bottom",affix;if(typeof offset!="object")offsetBottom=offsetTop=offset;if(typeof offsetTop=="function")offsetTop=offset.top();if(typeof offsetBottom=="function")offsetBottom=offset.bottom();affix=this.unpin!=null&&scrollTop+this.unpin<=position.top?false:offsetBottom!=null&&position.top+this.$element.height()>=scrollHeight-offsetBottom?"bottom":offsetTop!=null&&scrollTop<=offsetTop?"top":false;
if(this.affixed===affix)return;this.affixed=affix;this.unpin=affix=="bottom"?position.top-scrollTop:null;this.$element.removeClass(reset).addClass("affix"+(affix?"-"+affix:""))};var old=$.fn.affix;$.fn.affix=function(option){return this.each(function(){var $this=$(this),data=$this.data("affix"),options=typeof option=="object"&&option;if(!data)$this.data("affix",data=new Affix(this,options));if(typeof option=="string")data[option]()})};$.fn.affix.Constructor=Affix;$.fn.affix.defaults={offset:0};$.fn.affix.noConflict=
function(){$.fn.affix=old;return this};$(window).on("load",function(){$('[data-spy="affix"]').each(function(){var $spy=$(this),data=$spy.data();data.offset=data.offset||{};data.offsetBottom&&(data.offset.bottom=data.offsetBottom);data.offsetTop&&(data.offset.top=data.offsetTop);$spy.affix(data)})})}(window.jQuery);
!function($){var dismiss='[data-dismiss="alert"]',Alert=function(el){$(el).on("click",dismiss,this.close)};Alert.prototype.close=function(e){var $this=$(this),selector=$this.attr("data-target"),$parent;if(!selector){selector=$this.attr("href");selector=selector&&selector.replace(/.*(?=#[^\s]*$)/,"")}$parent=$(selector);e&&e.preventDefault();$parent.length||($parent=$this.hasClass("alert")?$this:$this.parent());$parent.trigger(e=$.Event("close"));if(e.isDefaultPrevented())return;$parent.removeClass("in");
function removeElement(){$parent.trigger("closed").remove()}$.support.transition&&$parent.hasClass("fade")?$parent.on($.support.transition.end,removeElement):removeElement()};var old=$.fn.alert;$.fn.alert=function(option){return this.each(function(){var $this=$(this),data=$this.data("alert");if(!data)$this.data("alert",data=new Alert(this));if(typeof option=="string")data[option].call($this)})};$.fn.alert.Constructor=Alert;$.fn.alert.noConflict=function(){$.fn.alert=old;return this};$(document).on("click.alert.data-api",
dismiss,Alert.prototype.close)}(window.jQuery);
!function($){var Button=function(element,options){this.$element=$(element);this.options=$.extend({},$.fn.button.defaults,options)};Button.prototype.setState=function(state){var d="disabled",$el=this.$element,data=$el.data(),val=$el.is("input")?"val":"html";state=state+"Text";data.resetText||$el.data("resetText",$el[val]());$el[val](data[state]||this.options[state]);setTimeout(function(){state=="loadingText"?$el.addClass(d).attr(d,d):$el.removeClass(d).removeAttr(d)},0)};Button.prototype.toggle=function(){var $parent=
this.$element.closest('[data-toggle="buttons-radio"]');$parent&&$parent.find(".active").removeClass("active");this.$element.toggleClass("active")};var old=$.fn.button;$.fn.button=function(option){return this.each(function(){var $this=$(this),data=$this.data("button"),options=typeof option=="object"&&option;if(!data)$this.data("button",data=new Button(this,options));if(option=="toggle")data.toggle();else if(option)data.setState(option)})};$.fn.button.defaults={loadingText:"loading..."};$.fn.button.Constructor=
Button;$.fn.button.noConflict=function(){$.fn.button=old;return this};$(document).on("click.button.data-api","[data-toggle^=button]",function(e){var $btn=$(e.target);if(!$btn.hasClass("btn"))$btn=$btn.closest(".btn");$btn.button("toggle")})}(window.jQuery);
!function($){var Collapse=function(element,options){this.$element=$(element);this.options=$.extend({},$.fn.collapse.defaults,options);if(this.options.parent)this.$parent=$(this.options.parent);this.options.toggle&&this.toggle()};Collapse.prototype={constructor:Collapse,dimension:function(){var hasWidth=this.$element.hasClass("width");return hasWidth?"width":"height"},show:function(){var dimension,scroll,actives,hasData;if(this.transitioning||this.$element.hasClass("in"))return;dimension=this.dimension();
scroll=$.camelCase(["scroll",dimension].join("-"));actives=this.$parent&&this.$parent.find("> .accordion-group > .in");if(actives&&actives.length){hasData=actives.data("collapse");if(hasData&&hasData.transitioning)return;actives.collapse("hide");hasData||actives.data("collapse",null)}this.$element[dimension](0);this.transition("addClass",$.Event("show"),"shown");$.support.transition&&this.$element[dimension](this.$element[0][scroll])},hide:function(){var dimension;if(this.transitioning||!this.$element.hasClass("in"))return;
dimension=this.dimension();this.reset(this.$element[dimension]());this.transition("removeClass",$.Event("hide"),"hidden");this.$element[dimension](0)},reset:function(size){var dimension=this.dimension();this.$element.removeClass("collapse")[dimension](size||"auto")[0].offsetWidth;this.$element[size!==null?"addClass":"removeClass"]("collapse");return this},transition:function(method,startEvent,completeEvent){var that=this,complete=function(){if(startEvent.type=="show")that.reset();that.transitioning=
0;that.$element.trigger(completeEvent)};this.$element.trigger(startEvent);if(startEvent.isDefaultPrevented())return;this.transitioning=1;this.$element[method]("in");$.support.transition&&this.$element.hasClass("collapse")?this.$element.one($.support.transition.end,complete):complete()},toggle:function(){this[this.$element.hasClass("in")?"hide":"show"]()}};var old=$.fn.collapse;$.fn.collapse=function(option){return this.each(function(){var $this=$(this),data=$this.data("collapse"),options=$.extend({},
$.fn.collapse.defaults,$this.data(),typeof option=="object"&&option);if(!data)$this.data("collapse",data=new Collapse(this,options));if(typeof option=="string")data[option]()})};$.fn.collapse.defaults={toggle:true};$.fn.collapse.Constructor=Collapse;$.fn.collapse.noConflict=function(){$.fn.collapse=old;return this};$(document).on("click.collapse.data-api","[data-toggle=collapse]",function(e){var $this=$(this),href,target=$this.attr("data-target")||e.preventDefault()||(href=$this.attr("href"))&&href.replace(/.*(?=#[^\s]+$)/,
""),option=$(target).data("collapse")?"toggle":$this.data();$this[$(target).hasClass("in")?"addClass":"removeClass"]("collapsed");$(target).collapse(option)})}(window.jQuery);
!function($){var Carousel=function(element,options){this.$element=$(element);this.$indicators=this.$element.find(".carousel-indicators");this.options=options;this.options.pause=="hover"&&this.$element.on("mouseenter",$.proxy(this.pause,this)).on("mouseleave",$.proxy(this.cycle,this))};Carousel.prototype={cycle:function(e){if(!e)this.paused=false;if(this.interval)clearInterval(this.interval);this.options.interval&&!this.paused&&(this.interval=setInterval($.proxy(this.next,this),this.options.interval));
return this},getActiveIndex:function(){this.$active=this.$element.find(".item.active");this.$items=this.$active.parent().children();return this.$items.index(this.$active)},to:function(pos){var activeIndex=this.getActiveIndex(),that=this;if(pos>this.$items.length-1||pos<0)return;if(this.sliding)return this.$element.one("slid",function(){that.to(pos)});if(activeIndex==pos)return this.pause().cycle();return this.slide(pos>activeIndex?"next":"prev",$(this.$items[pos]))},pause:function(e){if(!e)this.paused=
true;if(this.$element.find(".next, .prev").length&&$.support.transition.end){this.$element.trigger($.support.transition.end);this.cycle(true)}clearInterval(this.interval);this.interval=null;return this},next:function(){if(this.sliding)return;return this.slide("next")},prev:function(){if(this.sliding)return;return this.slide("prev")},slide:function(type,next){var $active=this.$element.find(".item.active"),$next=next||$active[type](),isCycling=this.interval,direction=type=="next"?"left":"right",fallback=
type=="next"?"first":"last",that=this,e;this.sliding=true;isCycling&&this.pause();$next=$next.length?$next:this.$element.find(".item")[fallback]();e=$.Event("slide",{relatedTarget:$next[0],direction:direction});if($next.hasClass("active"))return;if(this.$indicators.length){this.$indicators.find(".active").removeClass("active");this.$element.one("slid",function(){var $nextIndicator=$(that.$indicators.children()[that.getActiveIndex()]);$nextIndicator&&$nextIndicator.addClass("active")})}if($.support.transition&&
this.$element.hasClass("slide")){this.$element.trigger(e);if(e.isDefaultPrevented())return;$next.addClass(type);$next[0].offsetWidth;$active.addClass(direction);$next.addClass(direction);this.$element.one($.support.transition.end,function(){$next.removeClass([type,direction].join(" ")).addClass("active");$active.removeClass(["active",direction].join(" "));that.sliding=false;setTimeout(function(){that.$element.trigger("slid")},0)})}else{this.$element.trigger(e);if(e.isDefaultPrevented())return;$active.removeClass("active");
$next.addClass("active");this.sliding=false;this.$element.trigger("slid")}isCycling&&this.cycle();return this}};var old=$.fn.carousel;$.fn.carousel=function(option){return this.each(function(){var $this=$(this),data=$this.data("carousel"),options=$.extend({},$.fn.carousel.defaults,typeof option=="object"&&option),action=typeof option=="string"?option:options.slide;if(!data)$this.data("carousel",data=new Carousel(this,options));if(typeof option=="number")data.to(option);else if(action)data[action]();
else if(options.interval)data.pause().cycle()})};$.fn.carousel.defaults={interval:5E3,pause:"hover"};$.fn.carousel.Constructor=Carousel;$.fn.carousel.noConflict=function(){$.fn.carousel=old;return this};$(document).on("click.carousel.data-api","[data-slide], [data-slide-to]",function(e){var $this=$(this),href,$target=$($this.attr("data-target")||(href=$this.attr("href"))&&href.replace(/.*(?=#[^\s]+$)/,"")),options=$.extend({},$target.data(),$this.data()),slideIndex;$target.carousel(options);if(slideIndex=
$this.attr("data-slide-to"))$target.data("carousel").pause().to(slideIndex).cycle();e.preventDefault()})}(window.jQuery);
!function($){var Typeahead=function(element,options){this.$element=$(element);this.options=$.extend({},$.fn.typeahead.defaults,options);this.matcher=this.options.matcher||this.matcher;this.sorter=this.options.sorter||this.sorter;this.highlighter=this.options.highlighter||this.highlighter;this.updater=this.options.updater||this.updater;this.source=this.options.source;this.$menu=$(this.options.menu);this.shown=false;this.listen()};Typeahead.prototype={constructor:Typeahead,select:function(){var val=
this.$menu.find(".active").attr("data-value");this.$element.val(this.updater(val)).change();return this.hide()},updater:function(item){return item},show:function(){var pos=$.extend({},this.$element.position(),{height:this.$element[0].offsetHeight});this.$menu.insertAfter(this.$element).css({top:pos.top+pos.height,left:pos.left}).show();this.shown=true;return this},hide:function(){this.$menu.hide();this.shown=false;return this},lookup:function(event){var items;this.query=this.$element.val();if(!this.query||
this.query.length<this.options.minLength)return this.shown?this.hide():this;items=$.isFunction(this.source)?this.source(this.query,$.proxy(this.process,this)):this.source;return items?this.process(items):this},process:function(items){var that=this;items=$.grep(items,function(item){return that.matcher(item)});items=this.sorter(items);if(!items.length)return this.shown?this.hide():this;return this.render(items.slice(0,this.options.items)).show()},matcher:function(item){return~item.toLowerCase().indexOf(this.query.toLowerCase())},
sorter:function(items){var beginswith=[],caseSensitive=[],caseInsensitive=[],item;while(item=items.shift())if(!item.toLowerCase().indexOf(this.query.toLowerCase()))beginswith.push(item);else if(~item.indexOf(this.query))caseSensitive.push(item);else caseInsensitive.push(item);return beginswith.concat(caseSensitive,caseInsensitive)},highlighter:function(item){var query=this.query.replace(/[\-\[\]{}()*+?.,\\\^$|#\s]/g,"\\$&");return item.replace(new RegExp("("+query+")","ig"),function($1,match){return"<strong>"+
match+"</strong>"})},render:function(items){var that=this;items=$(items).map(function(i,item){i=$(that.options.item).attr("data-value",item);i.find("a").html(that.highlighter(item));return i[0]});items.first().addClass("active");this.$menu.html(items);return this},next:function(event){var active=this.$menu.find(".active").removeClass("active"),next=active.next();if(!next.length)next=$(this.$menu.find("li")[0]);next.addClass("active")},prev:function(event){var active=this.$menu.find(".active").removeClass("active"),
prev=active.prev();if(!prev.length)prev=this.$menu.find("li").last();prev.addClass("active")},listen:function(){this.$element.on("focus",$.proxy(this.focus,this)).on("blur",$.proxy(this.blur,this)).on("keypress",$.proxy(this.keypress,this)).on("keyup",$.proxy(this.keyup,this));if(this.eventSupported("keydown"))this.$element.on("keydown",$.proxy(this.keydown,this));this.$menu.on("click",$.proxy(this.click,this)).on("mouseenter","li",$.proxy(this.mouseenter,this)).on("mouseleave","li",$.proxy(this.mouseleave,
this))},eventSupported:function(eventName){var isSupported=eventName in this.$element;if(!isSupported){this.$element.setAttribute(eventName,"return;");isSupported=typeof this.$element[eventName]==="function"}return isSupported},move:function(e){if(!this.shown)return;switch(e.keyCode){case 9:case 13:case 27:e.preventDefault();break;case 38:e.preventDefault();this.prev();break;case 40:e.preventDefault();this.next();break}e.stopPropagation()},keydown:function(e){this.suppressKeyPressRepeat=~$.inArray(e.keyCode,
[40,38,9,13,27]);this.move(e)},keypress:function(e){if(this.suppressKeyPressRepeat)return;this.move(e)},keyup:function(e){switch(e.keyCode){case 40:case 38:case 16:case 17:case 18:break;case 9:case 13:if(!this.shown)return;this.select();break;case 27:if(!this.shown)return;this.hide();break;default:this.lookup()}e.stopPropagation();e.preventDefault()},focus:function(e){this.focused=true},blur:function(e){this.focused=false;if(!this.mousedover&&this.shown)this.hide()},click:function(e){e.stopPropagation();
e.preventDefault();this.select();this.$element.focus()},mouseenter:function(e){this.mousedover=true;this.$menu.find(".active").removeClass("active");$(e.currentTarget).addClass("active")},mouseleave:function(e){this.mousedover=false;if(!this.focused&&this.shown)this.hide()}};var old=$.fn.typeahead;$.fn.typeahead=function(option){return this.each(function(){var $this=$(this),data=$this.data("typeahead"),options=typeof option=="object"&&option;if(!data)$this.data("typeahead",data=new Typeahead(this,
options));if(typeof option=="string")data[option]()})};$.fn.typeahead.defaults={source:[],items:8,menu:'<ul class="typeahead dropdown-menu"></ul>',item:'<li><a href="#"></a></li>',minLength:1};$.fn.typeahead.Constructor=Typeahead;$.fn.typeahead.noConflict=function(){$.fn.typeahead=old;return this};$(document).on("focus.typeahead.data-api",'[data-provide="typeahead"]',function(e){var $this=$(this);if($this.data("typeahead"))return;$this.typeahead($this.data())})}(window.jQuery);;/**/
var $ = jQuery;
(function($){
	
	//closeDOMWindow
	$.fn.closeDOMWindow = function(settings){
		
		if(!settings){settings={};}
		
		var run = function(passingThis){
			
			if(settings.anchoredClassName){
				var $anchorClassName = $('.'+settings.anchoredClassName);
				$anchorClassName.fadeOut('fast',function(){
					if($.fn.draggable){
						$anchorClassName.draggable('destory').trigger("unload").remove();	
					}else{
						$anchorClassName.trigger("unload").remove();
					}
				});
				if(settings.functionCallOnClose){settings.functionCallAfterClose();}
			}else{
				var $DOMWindowOverlay = $('#DOMWindowOverlay');
				var $DOMWindow = $('#DOMWindow');
				$DOMWindowOverlay.fadeOut('fast',function(){
					$DOMWindowOverlay.trigger('unload').unbind().remove();																	  
				});
				$DOMWindow.fadeOut('fast',function(){
					if($.fn.draggable){
						$DOMWindow.draggable("destroy").trigger("unload").remove();
					}else{
						$DOMWindow.trigger("unload").remove();
					}
				});
			
				$(window).unbind('scroll.DOMWindow');
				$(window).unbind('resize.DOMWindow');
				
				if($.fn.openDOMWindow.isIE6){$('#DOMWindowIE6FixIframe').remove();}
				if(settings.functionCallOnClose){settings.functionCallAfterClose();}
			}	
		};
		
		if(settings.eventType){//if used with $().
			return this.each(function(index){
				$(this).bind(settings.eventType, function(){
					run(this);
					return false;
				});
			});
		}else{//else called as $.function
			run();
		}
		
	};
	
	//allow for public call, pass settings
	$.closeDOMWindow = function(s){$.fn.closeDOMWindow(s);};
	
	//openDOMWindow
	$.fn.openDOMWindow = function(instanceSettings){	
		
		var shortcut =  $.fn.openDOMWindow;
	
		//default settings combined with callerSettings////////////////////////////////////////////////////////////////////////
		
		shortcut.defaultsSettings = {
			anchoredClassName:'',
			anchoredSelector:'',
			borderColor:'#ccc',
			borderSize:'4',
			draggable:0,
			eventType:null, //click, blur, change, dblclick, error, focus, load, mousedown, mouseout, mouseup etc...
			fixedWindowY:100,
			functionCallOnOpen:null,
			functionCallOnClose:null,
			height:500,
			loader:0,
			loaderHeight:0,
			loaderImagePath:'',
			loaderWidth:0,
			modal:0,
			overlay:1,
			overlayColor:'#000',
			overlayOpacity:'85',
			positionLeft:0,
			positionTop:0,
			positionType:'centered', // centered, anchored, absolute, fixed
			width:500, 
			windowBGColor:'#fff',
			windowBGImage:null, // http path
			windowHTTPType:'get',
			windowPadding:10,
			windowSource:'inline', //inline, ajax, iframe
			windowSourceID:'',
			windowSourceURL:'',
			windowSourceAttrURL:'href'
		};
		
		var settings = $.extend({}, $.fn.openDOMWindow.defaultsSettings , instanceSettings || {});
		
		//Public functions
		
		shortcut.viewPortHeight = function(){ return self.innerHeight || document.documentElement.clientHeight || document.body.clientHeight;};
		shortcut.viewPortWidth = function(){ return self.innerWidth || document.documentElement.clientWidth || document.body.clientWidth;};
		shortcut.scrollOffsetHeight = function(){ return self.pageYOffset || document.documentElement.scrollTop || document.body.scrollTop;};
		shortcut.scrollOffsetWidth = function(){ return self.pageXOffset || document.documentElement.scrollLeft || document.body.scrollLeft;};
		shortcut.isIE6 = typeof document.body.style.maxHeight === "undefined";
		
		//Private Functions/////////////////////////////////////////////////////////////////////////////////////////////////////////
		
		var sizeOverlay = function(){
			var $DOMWindowOverlay = $('#DOMWindowOverlay');
			if(shortcut.isIE6){//if IE 6
				var overlayViewportHeight = document.documentElement.offsetHeight + document.documentElement.scrollTop - 4;
				var overlayViewportWidth = document.documentElement.offsetWidth - 21;
				$DOMWindowOverlay.css({'height':overlayViewportHeight +'px','width':overlayViewportWidth+'px'});
			}else{//else Firefox, safari, opera, IE 7+
				$DOMWindowOverlay.css({'height':'100%','width':'100%','position':'fixed'});
			}	
		};
		
		var sizeIE6Iframe = function(){
			var overlayViewportHeight = document.documentElement.offsetHeight + document.documentElement.scrollTop - 4;
			var overlayViewportWidth = document.documentElement.offsetWidth - 21;
			$('#DOMWindowIE6FixIframe').css({'height':overlayViewportHeight +'px','width':overlayViewportWidth+'px'});
		};
		
		var centerDOMWindow = function() {
			var $DOMWindow = $('#DOMWindow');
			if(settings.height + 50 > shortcut.viewPortHeight()){//added 50 to be safe
				$DOMWindow.css('left',Math.round(shortcut.viewPortWidth()/2) + shortcut.scrollOffsetWidth() - Math.round(($DOMWindow.outerWidth())/2));
			}else{
				$DOMWindow.css('left',Math.round(shortcut.viewPortWidth()/2) + shortcut.scrollOffsetWidth() - Math.round(($DOMWindow.outerWidth())/2));
				$DOMWindow.css('top',Math.round(shortcut.viewPortHeight()/2) + shortcut.scrollOffsetHeight() - Math.round(($DOMWindow.outerHeight())/2));
			}
		};
		
		var centerLoader = function() {
			var $DOMWindowLoader = $('#DOMWindowLoader');
			if(shortcut.isIE6){//if IE 6
				$DOMWindowLoader.css({'left':Math.round(shortcut.viewPortWidth()/2) + shortcut.scrollOffsetWidth() - Math.round(($DOMWindowLoader.innerWidth())/2),'position':'absolute'});
				$DOMWindowLoader.css({'top':Math.round(shortcut.viewPortHeight()/2) + shortcut.scrollOffsetHeight() - Math.round(($DOMWindowLoader.innerHeight())/2),'position':'absolute'});
			}else{
				$DOMWindowLoader.css({'left':'50%','top':'50%','position':'fixed'});
			}
			
		};
		
		var fixedDOMWindow = function(){
			var $DOMWindow = $('#DOMWindow');
			$DOMWindow.css('left', settings.positionLeft + shortcut.scrollOffsetWidth());
			$DOMWindow.css('top', + settings.positionTop + shortcut.scrollOffsetHeight());
		};
		
		var showDOMWindow = function(instance){
			if(arguments[0]){
				$('.'+instance+' #DOMWindowLoader').remove();
				$('.'+instance+' #DOMWindowContent').fadeIn('fast',function(){if(settings.functionCallOnOpen){settings.functionCallOnOpen();}});
				$('.'+instance+ '.closeDOMWindow').click(function(){
					$.closeDOMWindow();	
					return false;
				});
			}else{
				$('#DOMWindowLoader').remove();
				$('#DOMWindow').fadeIn('fast',function(){if(settings.functionCallOnOpen){settings.functionCallOnOpen();}});
				$('#DOMWindow .closeDOMWindow').click(function(){						
					$.closeDOMWindow();
					return false;
				});
			}
			
		};
		
		var urlQueryToObject = function(s){
			  var query = {};
			  s.replace(/b([^&=]*)=([^&=]*)b/g, function (m, a, d) {
				if (typeof query[a] != 'undefined') {
				  query[a] += ',' + d;
				} else {
				  query[a] = d;
				}
			  });
			  return query;
		};
			
		//Run Routine ///////////////////////////////////////////////////////////////////////////////////////////////////////////////
		var run = function(passingThis){
			
			//get values from element clicked, or assume its passed as an option
			settings.windowSourceID = $(passingThis).attr('href') || settings.windowSourceID;
			settings.windowSourceURL = $(passingThis).attr(settings.windowSourceAttrURL) || settings.windowSourceURL;
			settings.windowBGImage = settings.windowBGImage ? 'background-image:url('+settings.windowBGImage+')' : '';
			var urlOnly, urlQueryObject;
			
			if(settings.positionType == 'anchored'){//anchored DOM window
				
				var anchoredPositions = $(settings.anchoredSelector).position();
				var anchoredPositionX = anchoredPositions.left + settings.positionLeft;
				var anchoredPositionY = anchoredPositions.top + settings.positionTop;
				
				$('body').append('<div class="'+settings.anchoredClassName+'" style="'+settings.windowBGImage+';background-repeat:no-repeat;padding:'+settings.windowPadding+'px;overflow:auto;position:absolute;top:'+anchoredPositionY+'px;left:'+anchoredPositionX+'px;height:'+settings.height+'px;width:'+settings.width+'px;background-color:'+settings.windowBGColor+';border:'+settings.borderSize+'px solid '+settings.borderColor+';z-index:10001"><div id="DOMWindowContent" style="display:none"></div></div>');		
				//loader
				if(settings.loader && settings.loaderImagePath !== ''){
					$('.'+settings.anchoredClassName).append('<div id="DOMWindowLoader" style="width:'+settings.loaderWidth+'px;height:'+settings.loaderHeight+'px;"><img src="'+settings.loaderImagePath+'" /></div>');
					
				}

				if($.fn.draggable){
					if(settings.draggable){$('.' + settings.anchoredClassName).draggable({cursor:'move'});}
				}
				
				switch(settings.windowSource){
					case 'inline'://////////////////////////////// inline //////////////////////////////////////////
						$('.' + settings.anchoredClassName+" #DOMWindowContent").append($(settings.windowSourceID).children());
						$('.' + settings.anchoredClassName).unload(function(){// move elements back when you're finished
							$('.' + settings.windowSourceID).append( $('.' + settings.anchoredClassName+" #DOMWindowContent").children());				
						});
						showDOMWindow(settings.anchoredClassName);
					break;
					case 'iframe'://////////////////////////////// iframe //////////////////////////////////////////
						$('.' + settings.anchoredClassName+" #DOMWindowContent").append('<iframe frameborder="0" hspace="0" wspace="0" src="'+settings.windowSourceURL+'" name="DOMWindowIframe'+Math.round(Math.random()*1000)+'" style="width:100%;height:100%;border:none;background-color:#fff;" class="'+settings.anchoredClassName+'Iframe" ></iframe>');
						$('.'+settings.anchoredClassName+'Iframe').load(showDOMWindow(settings.anchoredClassName));
					break;
					case 'ajax'://////////////////////////////// ajax //////////////////////////////////////////	
						if(settings.windowHTTPType == 'post'){
							
							if(settings.windowSourceURL.indexOf("?") !== -1){//has a query string
								urlOnly = settings.windowSourceURL.substr(0, settings.windowSourceURL.indexOf("?"));
								urlQueryObject = urlQueryToObject(settings.windowSourceURL);
							}else{
								urlOnly = settings.windowSourceURL;
								urlQueryObject = {};
							}
							$('.' + settings.anchoredClassName+" #DOMWindowContent").load(urlOnly,urlQueryObject,function(){
								showDOMWindow(settings.anchoredClassName);
							});
						}else{
							if(settings.windowSourceURL.indexOf("?") == -1){ //no query string, so add one
								settings.windowSourceURL += '?';
							}
							$('.' + settings.anchoredClassName+" #DOMWindowContent").load(
								settings.windowSourceURL + '&random=' + (new Date().getTime()),function(){
								showDOMWindow(settings.anchoredClassName);
							});
						}
					break;
				}
				
			}else{//centered, fixed, absolute DOM window
				
				//overlay & modal
				if(settings.overlay){
					$('body').append('<div id="DOMWindowOverlay" style="z-index:10000;display:none;position:absolute;top:0;left:0;background-color:'+settings.overlayColor+';filter:alpha(opacity='+settings.overlayOpacity+');-moz-opacity: 0.'+settings.overlayOpacity+';opacity: 0.'+settings.overlayOpacity+';"></div>');
					if(shortcut.isIE6){//if IE 6
						$('body').append('<iframe id="DOMWindowIE6FixIframe"  src="blank.html"  style="width:100%;height:100%;z-index:9999;position:absolute;top:0;left:0;filter:alpha(opacity=0);"></iframe>');
						sizeIE6Iframe();
					}
					sizeOverlay();
					var $DOMWindowOverlay = $('#DOMWindowOverlay');
					$DOMWindowOverlay.fadeIn('fast');
					if(!settings.modal){$DOMWindowOverlay.click(function(){$.closeDOMWindow();});}
				}
				
				//loader
				if(settings.loader && settings.loaderImagePath !== ''){
					$('body').append('<div id="DOMWindowLoader" style="z-index:10002;width:'+settings.loaderWidth+'px;height:'+settings.loaderHeight+'px;"><img src="'+settings.loaderImagePath+'" /></div>');
					centerLoader();
				}

				//add DOMwindow
				$('body').append('<div id="DOMWindow" style="background-repeat:no-repeat;'+settings.windowBGImage+';overflow:auto;padding:'+settings.windowPadding+'px;display:none;height:'+settings.height+'px;width:'+settings.width+'px;background-color:'+settings.windowBGColor+';border:'+settings.borderSize+'px solid '+settings.borderColor+'; position:absolute;z-index:10001"></div>');
				
				var $DOMWindow = $('#DOMWindow');
				//centered, absolute, or fixed
				switch(settings.positionType){
					case 'centered':
						centerDOMWindow();
						if(settings.height + 50 > shortcut.viewPortHeight()){//added 50 to be safe
							$DOMWindow.css('top', (settings.fixedWindowY + shortcut.scrollOffsetHeight()) + 'px');
						}
					break;
					case 'absolute':
						$DOMWindow.css({'top':(settings.positionTop+shortcut.scrollOffsetHeight())+'px','left':(settings.positionLeft+shortcut.scrollOffsetWidth())+'px'});
						if($.fn.draggable){
							if(settings.draggable){$DOMWindow.draggable({cursor:'move'});}
						}
					break;
					case 'fixed':
						fixedDOMWindow();
					break;
					case 'anchoredSingleWindow':
						var anchoredPositions = $(settings.anchoredSelector).position();
						var anchoredPositionX = anchoredPositions.left + settings.positionLeft;
						var anchoredPositionY = anchoredPositions.top + settings.positionTop;
						$DOMWindow.css({'top':anchoredPositionY + 'px','left':anchoredPositionX+'px'});
								
					break;
				}
				
				$(window).bind('scroll.DOMWindow',function(){
					if(settings.overlay){sizeOverlay();}
					if(shortcut.isIE6){sizeIE6Iframe();}
					if(settings.positionType == 'centered'){centerDOMWindow();}
					if(settings.positionType == 'fixed'){fixedDOMWindow();}
				});

				$(window).bind('resize.DOMWindow',function(){
					if(shortcut.isIE6){sizeIE6Iframe();}
					if(settings.overlay){sizeOverlay();}
					if(settings.positionType == 'centered'){centerDOMWindow();}
				});
				
				switch(settings.windowSource){
					case 'inline'://////////////////////////////// inline //////////////////////////////////////////
						$DOMWindow.append($(settings.windowSourceID).children());
						$DOMWindow.unload(function(){// move elements back when you're finished
							$(settings.windowSourceID).append($DOMWindow.children());				
						});
						showDOMWindow();
					break;
					case 'iframe'://////////////////////////////// iframe //////////////////////////////////////////
						$DOMWindow.append('<iframe frameborder="0" hspace="0" wspace="0" src="'+settings.windowSourceURL+'" name="DOMWindowIframe'+Math.round(Math.random()*1000)+'" style="width:100%;height:100%;border:none;background-color:#fff;" id="DOMWindowIframe" ></iframe>');
						$('#DOMWindowIframe').load(showDOMWindow());
					break;
					case 'ajax'://////////////////////////////// ajax //////////////////////////////////////////
						if(settings.windowHTTPType == 'post'){
							
							if(settings.windowSourceURL.indexOf("?") !== -1){//has a query string
								urlOnly = settings.windowSourceURL.substr(0, settings.windowSourceURL.indexOf("?"));
								urlQueryObject = urlQueryToObject(settings.windowSourceURL);
							}else{
								urlOnly = settings.windowSourceURL;
								urlQueryObject = {};
							}
							$DOMWindow.load(urlOnly,urlQueryObject,function(){
								showDOMWindow();
							});
						}else{
							if(settings.windowSourceURL.indexOf("?") == -1){ //no query string, so add one
								settings.windowSourceURL += '?';
							}
							$DOMWindow.load(
								settings.windowSourceURL + '&random=' + (new Date().getTime()),function(){
								showDOMWindow();
							});
						}
					break;
				}
				
			}//end if anchored, or absolute, fixed, centered
			
		};//end run()
		
		if(settings.eventType){//if used with $().
			return this.each(function(index){				  
				$(this).bind(settings.eventType,function(){
					run(this);
					return false;
				});
			});	
		}else{//else called as $.function
			run();
		}
		
	};//end function openDOMWindow
	
	//allow for public call, pass settings
	$.openDOMWindow = function(s){$.fn.openDOMWindow(s);};
	
})(jQuery);
;/**/
/* Placeholders.js v2.1.1 */
(function(t){"use strict";function e(t,e,r){return t.addEventListener?t.addEventListener(e,r,!1):t.attachEvent?t.attachEvent("on"+e,r):void 0}function r(t,e){var r,n;for(r=0,n=t.length;n>r;r++)if(t[r]===e)return!0;return!1}function n(t,e){var r;t.createTextRange?(r=t.createTextRange(),r.move("character",e),r.select()):t.selectionStart&&(t.focus(),t.setSelectionRange(e,e))}function a(t,e){try{return t.type=e,!0}catch(r){return!1}}t.Placeholders={Utils:{addEventListener:e,inArray:r,moveCaret:n,changeType:a}}})(this),function(t){"use strict";function e(){}function r(t,e){var r,n,a=!!e&&t.value!==e,u=t.value===t.getAttribute(V);return(a||u)&&"true"===t.getAttribute(D)?(t.setAttribute(D,"false"),t.value=t.value.replace(t.getAttribute(V),""),t.className=t.className.replace(R,""),n=t.getAttribute(z),n&&(t.setAttribute("maxLength",n),t.removeAttribute(z)),r=t.getAttribute(I),r&&(t.type=r),!0):!1}function n(t){var e,r,n=t.getAttribute(V);return""===t.value&&n?(t.setAttribute(D,"true"),t.value=n,t.className+=" "+k,r=t.getAttribute(z),r||(t.setAttribute(z,t.maxLength),t.removeAttribute("maxLength")),e=t.getAttribute(I),e?t.type="text":"password"===t.type&&K.changeType(t,"text")&&t.setAttribute(I,"password"),!0):!1}function a(t,e){var r,n,a,u,i;if(t&&t.getAttribute(V))e(t);else for(r=t?t.getElementsByTagName("input"):p,n=t?t.getElementsByTagName("textarea"):h,i=0,u=r.length+n.length;u>i;i++)a=r.length>i?r[i]:n[i-r.length],e(a)}function u(t){a(t,r)}function i(t){a(t,n)}function l(t){return function(){b&&t.value===t.getAttribute(V)&&"true"===t.getAttribute(D)?K.moveCaret(t,0):r(t)}}function o(t){return function(){n(t)}}function c(t){return function(e){return m=t.value,"true"===t.getAttribute(D)&&m===t.getAttribute(V)&&K.inArray(C,e.keyCode)?(e.preventDefault&&e.preventDefault(),!1):void 0}}function s(t){return function(){r(t,m),""===t.value&&(t.blur(),K.moveCaret(t,0))}}function d(t){return function(){t===document.activeElement&&t.value===t.getAttribute(V)&&"true"===t.getAttribute(D)&&K.moveCaret(t,0)}}function g(t){return function(){u(t)}}function v(t){t.form&&(L=t.form,L.getAttribute(P)||(K.addEventListener(L,"submit",g(L)),L.setAttribute(P,"true"))),K.addEventListener(t,"focus",l(t)),K.addEventListener(t,"blur",o(t)),b&&(K.addEventListener(t,"keydown",c(t)),K.addEventListener(t,"keyup",s(t)),K.addEventListener(t,"click",d(t))),t.setAttribute(U,"true"),t.setAttribute(V,E),n(t)}var p,h,b,f,m,A,y,E,x,L,T,N,S,w=["text","search","url","tel","email","password","number","textarea"],C=[27,33,34,35,36,37,38,39,40,8,46],B="#ccc",k="placeholdersjs",R=RegExp("(?:^|\\s)"+k+"(?!\\S)"),V="data-placeholder-value",D="data-placeholder-active",I="data-placeholder-type",P="data-placeholder-submit",U="data-placeholder-bound",j="data-placeholder-focus",q="data-placeholder-live",z="data-placeholder-maxlength",F=document.createElement("input"),G=document.getElementsByTagName("head")[0],H=document.documentElement,J=t.Placeholders,K=J.Utils;if(J.nativeSupport=void 0!==F.placeholder,!J.nativeSupport){for(p=document.getElementsByTagName("input"),h=document.getElementsByTagName("textarea"),b="false"===H.getAttribute(j),f="false"!==H.getAttribute(q),A=document.createElement("style"),A.type="text/css",y=document.createTextNode("."+k+" { color:"+B+"; }"),A.styleSheet?A.styleSheet.cssText=y.nodeValue:A.appendChild(y),G.insertBefore(A,G.firstChild),S=0,N=p.length+h.length;N>S;S++)T=p.length>S?p[S]:h[S-p.length],E=T.attributes.placeholder,E&&(E=E.nodeValue,E&&K.inArray(w,T.type)&&v(T));x=setInterval(function(){for(S=0,N=p.length+h.length;N>S;S++)T=p.length>S?p[S]:h[S-p.length],E=T.attributes.placeholder,E&&(E=E.nodeValue,E&&K.inArray(w,T.type)&&(T.getAttribute(U)||v(T),(E!==T.getAttribute(V)||"password"===T.type&&!T.getAttribute(I))&&("password"===T.type&&!T.getAttribute(I)&&K.changeType(T,"text")&&T.setAttribute(I,"password"),T.value===T.getAttribute(V)&&(T.value=E),T.setAttribute(V,E))));f||clearInterval(x)},100)}J.disable=J.nativeSupport?e:u,J.enable=J.nativeSupport?e:i}(this);;/**/
/*!
 * Retina.js v1.3.0
 *
 * Copyright 2014 Imulus, LLC
 * Released under the MIT license
 *
 * Retina.js is an open source script that makes it easy to serve
 * high-resolution images to devices with retina displays.
 */
!function(){function a(){}function b(a){return f.retinaImageSuffix+a}function c(a,c){if(this.path=a||"","undefined"!=typeof c&&null!==c)this.at_2x_path=c,this.perform_check=!1;else{if(void 0!==document.createElement){var d=document.createElement("a");d.href=this.path,d.pathname=d.pathname.replace(g,b),this.at_2x_path=d.href}else{var e=this.path.split("?");e[0]=e[0].replace(g,b),this.at_2x_path=e.join("?")}this.perform_check=!0}}function d(a){this.el=a,this.path=new c(this.el.getAttribute("src"),this.el.getAttribute("data-at2x"));var b=this;this.path.check_2x_variant(function(a){a&&b.swap()})}var e="undefined"==typeof exports?window:exports,f={retinaImageSuffix:"@2x",check_mime_type:!0,force_original_dimensions:!0};e.Retina=a,a.configure=function(a){null===a&&(a={});for(var b in a)a.hasOwnProperty(b)&&(f[b]=a[b])},a.init=function(a){null===a&&(a=e);var b=a.onload||function(){};a.onload=function(){var a,c,e=document.getElementsByTagName("img"),f=[];for(a=0;a<e.length;a+=1)c=e[a],c.getAttributeNode("data-no-retina")||f.push(new d(c));b()}},a.isRetina=function(){var a="(-webkit-min-device-pixel-ratio: 1.5), (min--moz-device-pixel-ratio: 1.5), (-o-min-device-pixel-ratio: 3/2), (min-resolution: 1.5dppx)";return e.devicePixelRatio>1?!0:e.matchMedia&&e.matchMedia(a).matches?!0:!1};var g=/\.\w+$/;e.RetinaImagePath=c,c.confirmed_paths=[],c.prototype.is_external=function(){return!(!this.path.match(/^https?\:/i)||this.path.match("//"+document.domain))},c.prototype.check_2x_variant=function(a){var b,d=this;return this.is_external()?a(!1):this.perform_check||"undefined"==typeof this.at_2x_path||null===this.at_2x_path?this.at_2x_path in c.confirmed_paths?a(!0):(b=new XMLHttpRequest,b.open("HEAD",this.at_2x_path),b.onreadystatechange=function(){if(4!==b.readyState)return a(!1);if(b.status>=200&&b.status<=399){if(f.check_mime_type){var e=b.getResponseHeader("Content-Type");if(null===e||!e.match(/^image/i))return a(!1)}return c.confirmed_paths.push(d.at_2x_path),a(!0)}return a(!1)},b.send(),void 0):a(!0)},e.RetinaImage=d,d.prototype.swap=function(a){function b(){c.el.complete?(f.force_original_dimensions&&(c.el.setAttribute("width",c.el.offsetWidth),c.el.setAttribute("height",c.el.offsetHeight)),c.el.setAttribute("src",a)):setTimeout(b,5)}"undefined"==typeof a&&(a=this.path.at_2x_path);var c=this;b()},a.isRetina()&&a.init(e)}();;/**/
/*!
 * JavaScript Cookie v2.0.3
 * https://github.com/js-cookie/js-cookie
 *
 * Copyright 2006, 2015 Klaus Hartl & Fagner Brack
 * Released under the MIT license
 */
(function (factory) {
	if (typeof define === 'function' && define.amd) {
		define(factory);
	} else if (typeof exports === 'object') {
		module.exports = factory();
	} else {
		var _OldCookies = window.Cookies;
		var api = window.Cookies = factory(window.jQuery);
		api.noConflict = function () {
			window.Cookies = _OldCookies;
			return api;
		};
	}
}(function () {
	function extend () {
		var i = 0;
		var result = {};
		for (; i < arguments.length; i++) {
			var attributes = arguments[ i ];
			for (var key in attributes) {
				result[key] = attributes[key];
			}
		}
		return result;
	}

	function init (converter) {
		function api (key, value, attributes) {
			var result;

			// Write

			if (arguments.length > 1) {
				attributes = extend({
					path: '/'
				}, api.defaults, attributes);

				if (typeof attributes.expires === 'number') {
					var expires = new Date();
					expires.setMilliseconds(expires.getMilliseconds() + attributes.expires * 864e+5);
					attributes.expires = expires;
				}

				try {
					result = JSON.stringify(value);
					if (/^[\{\[]/.test(result)) {
						value = result;
					}
				} catch (e) {}

				value = encodeURIComponent(String(value));
				value = value.replace(/%(23|24|26|2B|3A|3C|3E|3D|2F|3F|40|5B|5D|5E|60|7B|7D|7C)/g, decodeURIComponent);

				key = encodeURIComponent(String(key));
				key = key.replace(/%(23|24|26|2B|5E|60|7C)/g, decodeURIComponent);
				key = key.replace(/[\(\)]/g, escape);

				return (document.cookie = [
					key, '=', value,
					attributes.expires && '; expires=' + attributes.expires.toUTCString(), // use expires attribute, max-age is not supported by IE
					attributes.path    && '; path=' + attributes.path,
					attributes.domain  && '; domain=' + attributes.domain,
					attributes.secure ? '; secure' : ''
				].join(''));
			}

			// Read

			if (!key) {
				result = {};
			}

			// To prevent the for loop in the first place assign an empty array
			// in case there are no cookies at all. Also prevents odd result when
			// calling "get()"
			var cookies = document.cookie ? document.cookie.split('; ') : [];
			var rdecode = /(%[0-9A-Z]{2})+/g;
			var i = 0;

			for (; i < cookies.length; i++) {
				var parts = cookies[i].split('=');
				var name = parts[0].replace(rdecode, decodeURIComponent);
				var cookie = parts.slice(1).join('=');

				if (cookie.charAt(0) === '"') {
					cookie = cookie.slice(1, -1);
				}

				try {
					cookie = converter && converter(cookie, name) || cookie.replace(rdecode, decodeURIComponent);

					if (this.json) {
						try {
							cookie = JSON.parse(cookie);
						} catch (e) {}
					}

					if (key === name) {
						result = cookie;
						break;
					}

					if (!key) {
						result[name] = cookie;
					}
				} catch (e) {}
			}

			return result;
		}

		api.get = api.set = api;
		api.getJSON = function () {
			return api.apply({
				json: true
			}, [].slice.call(arguments));
		};
		api.defaults = {};

		api.remove = function (key, attributes) {
			api(key, '', extend(attributes, {
				expires: -1
			}));
		};

		api.withConverter = init;

		return api;
	}

	return init();
}));
;/**/
this.console=this.console||{info:function(){},log:function(){},dir:function(){},debug:function(){},warn:function(){},error:function(){}}
;/**/
jQuery(function($){if($(".vertical-menu-list").length&&$(".global-services").length)$(".vertical-menu-list a").click(function(){var linkText=$(this).text();sendCustomTrackingEvent("event","Left Navigation","Click",linkText)});if($(".vertical-tabs .side-nav").length)$(".vertical-tabs .side-nav a").click(function(){var linkText=$(this).text();sendCustomTrackingEvent("event","Left Navigation","Click",linkText)});if($(".vertical-tabs .span3 ul").length)$(".vertical-tabs .span3 ul a.btn").click(function(){var linkText=
$(this).text();sendCustomTrackingEvent("event","Left Navigation","Click",linkText)});if($("video").length&&$("video").attr("data-event-tracking")=="true"){var trackingId="";$("video").on("play",function(e){if($(this).attr("id").length)trackingId=$(this).attr("id");else if($(this).children().attr("src").length)trackingId=$(this).children().attr("src");else trackingId=window.location.path;sendCustomTrackingEvent("event","Video","Play",trackingId)})}Drupal.behaviors.updateGoogleFormEvent={attach:function(context,
settings){$("form",context).bind("submit.ga",function(){var form=$(this);var formid=form.attr("id");sendCustomTrackingEvent("event","Forms","Submit",formid);form.unbind("submit.ga");form.submit()})}};if($(".span3 video").length)$(document).on("webkitfullscreenchange mozfullscreenchange fullscreenchange",function(e){$("video").toggleClass("fullscreen")});if($(".committee-chart").length)if(window.innerWidth<768)rebuildTableForMobile();if($(".signup-wrap").length){enterToClick($(".signup-wrap input"));
$("#block-webform-client-block-3332207").on("shown",function(){sendCustomTrackingEvent("event","Modal","Opened","Nanochip Fab Solutions Subscribe")})}if($(".js-link-pane-title").length){$(".js-link-pane-title").click(function(){var href=$(this).children(".pane-title").siblings(".pane-content").first().find(".block-bg").attr("href");window.location.href=href});$(".js-link-pane-title h2").hover(function(){$(this).toggleClass("js-hover-class")});$(".js-link-pane-title .block-bg").hover(function(){console.log("test hover");
$(this).parentsUntil(".pane-custom").siblings(".pane-title").toggleClass("js-hover-class")})}$(function(){$("#hero-banner-carousel").carousel({interval:5E3});setTimeout(function(){var bannerImgHeight=$("#hero-banner-carousel img").height();if(bannerImgHeight>0)$("#hero-banner-carousel .hero-slide").css("min-height",bannerImgHeight);$(window).resize(function(){$(".carousel").carousel("pause");var bannerImgHeight=$("#hero-banner-carousel img").height();if(bannerImgHeight>0)$("#hero-banner-carousel .hero-slide").css("min-height",
bannerImgHeight)})},250)});$("#edit-search-block-form--2").attr("placeholder","");$(".webform-client-form").unbind();var is_firefox=navigator.userAgent.toLowerCase().indexOf("firefox")>-1;if(is_firefox){var ss=document.createElement("link");ss.type="text/css";ss.rel="stylesheet";ss.href="http://vjs.zencdn.net/4.3/video-js.css";$("body").append(ss);var s=document.createElement("script");s.type="text/javascript";s.src="http://vjs.zencdn.net/4.3/video.js";$("body").append(s);if($("#pilot_careers_video").length){setTimeout(function(){$("#pilot_careers_video").removeClass("vjs-controls-disabled");
$("#pilot_careers_video .vjs-poster").show()},1500);$("#pilot_careers_video").click(function(){$("#pilot_careers_video .vjs-poster").hide()})}}if($.browser.msie&&parseInt($.browser.version,10)<=8)if($("#pilot_careers_video").length){setTimeout(function(){$("#pilot_careers_video").removeClass("vjs-controls-disabled");$("#pilot_careers_video .vjs-poster").show()},1500);$("#pilot_careers_video").click(function(){$("#pilot_careers_video .vjs-poster").hide()})}if(/Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent)){$(".feedback-container a").removeAttr("data-toggle");
$(".feedback-container a").attr("href","/feedback");setTimeout(function(){$(".captcha img").attr("height",60);$(".captcha img").attr("width",180)},2500);if(/iPad/i.test(navigator.userAgent)){$(".video video").addClass("ipad");$(".video-play-button").remove()}if(/iPhone/i.test(navigator.userAgent))$(".video-play-button").remove();$(".mobile .products-technologies").attr("href","javascript:;")}var feedbackURL=window.location.href;$("#webform-client-form-3332019").attr("action",feedbackURL);$("ul.menu.nav .dropdown-menu a.dropdown-toggle").click(function(){window.location.href=
$(this).attr("href")});if(window.innerWidth>1024){$(".prod-wrap").on("mouseover",function(){$(this).children(".prod-description").fadeIn()});$(".prod-wrap").on("mouseleave",function(){$(this).children(".prod-description").fadeOut()})}$(".vertical-tabs .panel-col-right .panel-pane").first().addClass("current-tab");$(".vertical-tabs .panel-col-left li").first().addClass("current");$(".vertical-tabs .panel-col-left li").click(function(e){if($("a",this).hasClass("request-information-cta"))return true;
$(".current-tab").removeClass("current-tab");$(".current").removeClass("current");$(".panel-col-right .panel-pane").eq($(this).index()).addClass("current-tab");$(this).addClass("current");e.preventDefault()});var tabsInterior=$(".vertical-tabs .panel-col-right .tab-content");if(tabsInterior.length>0){var verticalTabs=$(".vertical-tabs .panel-col-left .field-content");$(".vertical-tabs .panel-col-right .panel-pane").css("display","block");$(".current-tab").removeClass("current-tab");tabsInterior.first().addClass("current-tab");
verticalTabs.first().addClass("current");verticalTabs.click(function(e){$(".current-tab").removeClass("current-tab");$(".current").removeClass("current");tabsInterior.eq($(this).parent().parent().index()).addClass("current-tab");$(this).addClass("current");e.preventDefault()})}var agsTabs=$(".node-software .ags-content .ags-tab");if(agsTabs.length>0){agsTabs.first().addClass("current-tab");$(".node-software .vertical-menu-list li").first().addClass("current");$(".node-software .vertical-menu-list li").click(function(e){$(".current-tab").removeClass("current-tab");
$(".current").removeClass("current");agsTabs.eq($(this).index()).addClass("current-tab");$(this).addClass("current");e.preventDefault()})}var agsServiceTabs=$(".node-service .ags-content .ags-tab");if(agsServiceTabs.length>0){agsServiceTabs.first().addClass("current-tab");$(".node-service .vertical-menu-list li").first().addClass("current");$(".node-service .vertical-menu-list li").click(function(e){$(".current-tab").removeClass("current-tab");$(".current").removeClass("current");agsServiceTabs.eq($(this).index()).addClass("current-tab");
$(this).addClass("current");e.preventDefault()})}var hash=window.location.hash;if(hash){var clean_text=hash.substring(1);var text=clean_text.split("+");if(text[0]=="loc"){$(".view-amat2-locations .tab-content").removeClass("current-tab");$(".view-amat2-locations .tab-content").each(function(){var getH3=$(this).children("h3").text();getH3=getH3.toLowerCase();getH3=getH3.replace(" ","-");if(getH3==text[1])$(this).addClass("current-tab")});$(".view-amat2-locations .views-field-field-country-country-name .field-content").removeClass("current");
$(".view-amat2-locations .views-field-field-country-country-name .field-content").each(function(){var getFieldName=$(this).children(".btn").text();getFieldName=getFieldName.toLowerCase();getFieldName=getFieldName.replace(" ","-");if(getFieldName==text[1])$(this).addClass("current")})}}var verticalTabsExist=$("body").hasClass("vertical-tabs");if(verticalTabsExist){var urlhash;urlhash=window.location.hash;var matchFound=false;var countTab=0;$(".vertical-menu-list li a").each(function(){var linkHash=
$(this).attr("href");if(urlhash==linkHash){matchFound=true;return false}countTab++});if(matchFound){$(".current-tab").removeClass("current-tab");$(".current").removeClass("current");$(".panel-col-right .panel-pane").eq(countTab).addClass("current-tab");$(".vertical-menu-list li").eq(countTab).addClass("current")}}$(".investor-relations-block .ir-main-tab li").click(function(e){$(".investor-relations-block > .current-tab").removeClass("current-tab");$(".ir-main-tab .current").removeClass("current");
$(".investor-tab").eq($(this).index()).addClass("current-tab");$(this).addClass("current");e.preventDefault()});$(".investor-relations-block .ir-sub-tab li").click(function(e){$(".quarterly-earnings-feed > .current-tab").removeClass("current-tab");$(".ir-sub-tab .current").removeClass("current");$(".quarterly-earnings-tab").eq($(this).index()).addClass("current-tab");$(this).addClass("current");e.preventDefault()});$(".investor-relations-block .ir-sub-tab-reports li").click(function(e){$(".amat-ir-reports-years > .current-tab").removeClass("current-tab");
$(".ir-sub-tab-reports .current").removeClass("current");$(".annual-reports-tab").eq($(this).index()).addClass("current-tab");$(this).addClass("current");e.preventDefault()});$("#awards-landing-filter .btn").live("click",function(event){var selectedBtn=$(this).attr("value");loadingSpinner($(".view-id-view_awards_landing .view-content"),$(".view-id-view_awards_landing"));$("#edit-field-award-category-value").val(selectedBtn);$("#edit-submit-view-awards-landing").click();$("#awards-landing-filter a").each(function(){if($(this).hasClass("btn-current"))$(this).removeClass("btn-current")});
$(this).addClass("btn-current")});var pathname=window.location.pathname;var path_split=pathname.split("/");var section_nav=$(".section-navigation").length;var main_landing=$(".hero-slides").length;if(section_nav){$(".section-navigation .nav-links a").each(function(){var subnav_links=$(this).text().toLowerCase();var match_found=$.inArray(subnav_links,path_split);if(match_found>-1){if(path_split[1]=="zh-hans"||path_split[1]=="zh-hant"||path_split[1]=="ja"||path_split[1]=="ko"||path_split[1]=="en-in"||
path_split[1]=="en-sg")var i=2;else var i=1;if(path_split[i]=="global-services")$(this).each(function(){if($(this).text().toLowerCase()==path_split[i+1])$(this).addClass("active")});else $(this).addClass("active")}});$(window).resize(fixedHeader).trigger("resize")}function applyFunctionFilter(event){if(event)event.preventDefault();$(".form-item-field-location-cat-tid-1 .form-text").val("");$("#function-filter").val("Sales, Service and Field Support");$(".views-widget-filter-field_location_cat_tid_1 .form-text").val('"Sales, Service and Field Support"');
var $globalServicesLink=$(".subnav-globalservicessales");var $locationsLink=$(".subnav-locations");$locationsLink.removeClass("active");$globalServicesLink.addClass("active");Cookies.remove("global-services");$("#locations_page .views-submit-button .btn").trigger("click")}function clearFilterInputs(){$(".form-item-field-location-cat-tid-1 .form-text").val("")}function applyCookieAndGoToForm(event){event.preventDefault();console.log("settig cookie and redirecting..");Cookies.set("global-services",
"true");window.location.replace($(this).attr("href"))}LocationsPageLogic:{if(section_nav){if(Cookies.get("global-services")&&$.inArray("locations",pathname.split("/")))applyFunctionFilter();var $globalServicesLink=$(".subnav-globalservicessales");var $locationsLink=$(".subnav-locations");if(!$globalServicesLink)break LocationsPageLogic;$globalServicesLink.removeClass("active");if($.inArray("locations",pathname.split("/")))$globalServicesLink.on("click",applyFunctionFilter);else $globalServicesLink.on("click",
applyCookieAndGoToForm)}$(".globalservicesampsales").click(function(){Cookies.set("global-services","true")});var locationHash=window.location.hash;var path_array=pathname.split("/");if(path_array[3]=="locations"){clearFilterInputs();if(locationHash=="#services-sales"){$("#region-filter").val("All");$("#function-filter").val("Sales, Service and Field Support");$(".form-item-field-location-cat-tid-1 .form-text").val('"Sales, Service and Field Support"')}else{$(".form-item-field-location-cat-tid .form-text").val("United States");
$(".form-item-field-location-cat-tid-1 .form-text").val("Main Office")}$("#locations_page .views-submit-button .btn").trigger("click")}if(path_array[4]=="locations"){clearFilterInputs();if(path_array[1]=="ja"){console.log("ja");$(".form-item-field-location-cat-tid .form-text").val("Japan")}if(path_array[1]=="zh-hans")$(".form-item-field-location-cat-tid .form-text").val("China");if(path_array[1]=="zh-hant")$(".form-item-field-location-cat-tid .form-text").val("Taiwan");if(path_array[1]=="en-in")$(".form-item-field-location-cat-tid .form-text").val("India");
if(path_array[1]=="en-sg")$(".form-item-field-location-cat-tid .form-text").val("Southeast Asia");if(path_array[1]=="ko")$(".form-item-field-location-cat-tid .form-text").val("Korea");if(locationHash=="#services-sales"){$("#function-filter").val("Sales, Service and Field Support");$(".form-item-field-location-cat-tid-1 .form-text").val('"Sales, Service and Field Support"')}$("#locations_page .views-submit-button .btn").trigger("click")}}function fixedHeader(){var window_width=window.innerWidth;if(window_width<
980){$(window).unbind("scroll.fixedHeader");mobileHeader()}if(window_width>979){if(!main_landing){$(window).unbind("scroll.fixedHeader");childLandingHeader()}if(main_landing){$(window).unbind("scroll.fixedHeader");mainLandingHeader()}}}function mainLandingHeader(){var admin_bar=$(".admin-menu").length;var mainLandingHeaderScroll="";if(!admin_bar){$("body").removeClass("fixed-header");var mainLandingHeaderScroll=function(){var scroll=$(window).scrollTop();var elementOffset=$(".hero-slides .nav-links").offset().top;
var distance=$(".header-nav-wrap").height();var window_width=window.innerWidth;if(scroll>=distance&&window_width>979){$(".section-navigation").addClass("fixed");$("body").addClass("fixed-header");$(".section-navigation").show();$("#hero-banner-carousel .nav-links, .hero-link-wrap").addClass("hidden");setTimeout(function(){$(".section-navigation").addClass("animate")},1E3)}if(scroll<=distance&&window_width>979){$("body").removeClass("fixed-header");$(".section-navigation").hide();$(".section-navigation").removeClass("fixed");
$(".section-navigation").removeClass("animate");$("#hero-banner-carousel .nav-links, .hero-link-wrap").removeClass("hidden")}};$(window).bind("scroll.fixedHeader",mainLandingHeaderScroll)}return mainLandingHeaderScroll}function childLandingHeader(){var admin_bar=$(".admin-menu").length;if(!admin_bar){var checkScrollDistance=function(){var scroll=$(window).scrollTop();var initialDistance=$(".header-navbar").height();if($(".admin-menu").length)initialDistance=340;if(scroll>initialDistance)$(".section-navigation").addClass("fixed")};
checkScrollDistance();$("body").removeClass("fixed-header");var childLandingHeaderScroll=function(){var scroll=$(window).scrollTop();var elementOffset=$(".section-navigation").offset().top;var distance=$(".header-navbar").height();if(scroll>=distance){$(".section-navigation").addClass("fixed");$("body").addClass("fixed-header-desktop");setTimeout(function(){$(".section-navigation").addClass("animate")},1E3)}else{$(".section-navigation").removeClass("fixed");$("body").removeClass("fixed-header-desktop");
$(".section-navigation").removeClass("animate")}};$(window).bind("scroll.fixedHeader",childLandingHeaderScroll)}}function mobileHeader(){var previousScroll=0;$(".section-navigation").removeClass("fixed");var mobileHeaderScroll=function(){var currentScroll=$(this).scrollTop();if(currentScroll>previousScroll&&currentScroll>75){$("body").removeClass("fixed-header");$(".header-nav-wrap").removeClass("fixed")}if(currentScroll<5){$("body").removeClass("fixed-header");$(".header-nav-wrap").removeClass("fixed")}if(currentScroll<
previousScroll){$("body").addClass("fixed-header");$(".header-nav-wrap").addClass("fixed")}previousScroll=currentScroll};$(window).bind("scroll.fixedHeader",mobileHeaderScroll);return mobileHeaderScroll}var products_page=false;var anyparts_page=false;var main_parts=false;var req_quote=false;var product_library=false;var product_listing=false;var media_center=false;var locations_ww=false;var request_info_form=false;var main_search=false;var ir_news_search=false;var av_portfolio_search=false;var safe_harbor_page=
false;var subscribe_page=false;var endura_ventura_pvd=false;if($.inArray("products",path_split)>-1&&$.inArray("endura-ventura-pvd",path_split)>-1)var endura_ventura_pvd=true;if($.inArray("products",path_split)>-1)var products_page=true;if($.inArray("product-library",path_split)>-1)var product_library=true;if($.inArray("listing",path_split)>-1)var product_listing=true;if($.inArray("parts",path_split)>-1||$.inArray("parts-center",path_split)>-1)var any_parts=true;if($.inArray("parts-center",path_split)>
-1)var main_parts=true;if($.inArray("parts",path_split)>-1)var prod_parts=true;if($.inArray("request-quote",path_split)>-1)var req_quote=true;if($.inArray("media-center",path_split)>-1)var media_center=true;if($.inArray("request-information",path_split)>-1)var request_info_form=true;if($.inArray("search",path_split)>-1)var main_search=true;if($.inArray("investor-relations",path_split)>-1&&$.inArray("news",path_split)>-1)var ir_news_search=true;if($.inArray("applied-ventures",path_split)>-1&&$.inArray("portfolio",
path_split)>-1)var av_portfolio_search=true;if($.inArray("news",path_split)>-1&&$.inArray("events",path_split)>-1)var safe_harbor_page=true;if($.inArray("contact",path_split)>-1&&$.inArray("subscribe",path_split)>-1)var subscribe_page=true;if(subscribe_page)if($.browser.msie&&parseInt($.browser.version,10)<=8){$("#amat-utilities-nanochip-tech-form #edit-email--2").keydown(function(e){if(e.which==13){e.preventDefault();$("#amat-utilities-nanochip-tech-form button.form-submit").mousedown()}});$("#amat-utilities-nanochip-fab-form #edit-email").keydown(function(e){if(e.which==
13){e.preventDefault();$("#amat-utilities-nanochip-fab-form button.form-submit").mousedown()}})}else{$("#amat-utilities-nanochip-tech-form").change(function(){$("#amat-utilities-nanochip-tech-form button.form-submit").mousedown()});$("#amat-utilities-nanochip-fab-form").change(function(){$("#amat-utilities-nanochip-fab-form .form-submit").mousedown()})}if(safe_harbor_page)$(".section-navigation a").removeClass("active");if(av_portfolio_search){var searchIconMarkup='<a class="parts-search-icon" href="javascript:;">&nbsp;</a>';
$(".company-applied-ventures-portfolio .form-type-textfield .controls input").attr("placeholder","Search");$(".company-applied-ventures-portfolio .form-type-textfield .controls").append(searchIconMarkup);$(".company-applied-ventures-portfolio .form-type-textfield .controls input").change(function(){if($.browser.msie&&parseInt($.browser.version,10)<=8){var inputVal=$("#edit-title").val();if(inputVal=="Search")$("#edit-title").val("")}$(".company-applied-ventures-portfolio .views-submit-button button").click();
loadingSpinner($(".view-id-amat2_ventures_portfolio .view-content"),$(".view-id-amat2_ventures_portfolio"))});$(".parts-search-icon").click(function(){loadingSpinner($(".view-id-amat2_ventures_portfolio .view-content"),$(".view-id-amat2_ventures_portfolio"));if($.browser.msie&&parseInt($.browser.version,10)<=8){var inputVal=$("#edit-title").val();if(inputVal=="Search")$("#edit-title").val("")}$(".company-applied-ventures-portfolio .views-submit-button button").click()});Drupal.behaviors.updateAVPortfolioSearch=
{attach:function(context,settings){var searchIconMarkup='<a class="parts-search-icon" href="javascript:;">&nbsp;</a>';$(".company-applied-ventures-portfolio .form-type-textfield .controls input").attr("placeholder","Search");$(".company-applied-ventures-portfolio .form-type-textfield .controls").append(searchIconMarkup);$(".parts-search-icon:gt(0)").remove();$(".company-applied-ventures-portfolio .form-type-textfield .controls input").change(function(){$(".company-applied-ventures-portfolio .views-submit-button button").click();
loadingSpinner($(".view-id-amat2_ventures_portfolio .view-content"),$(".view-id-amat2_ventures_portfolio"))});$(".parts-search-icon").click(function(){if($.browser.msie&&parseInt($.browser.version,10)<=8){var inputVal=$("#edit-title").val();if(inputVal=="Search")$("#edit-title").val("")}$(".company-applied-ventures-portfolio .views-submit-button button").click();loadingSpinner($(".view-id-amat2_ventures_portfolio .view-content"),$(".view-id-amat2_ventures_portfolio"))})}}}if(ir_news_search){var searchIconMarkup=
'<a class="parts-search-icon" href="javascript:;">&nbsp;</a>';$(".company-investor-relations-news .form-type-textfield .controls input").attr("placeholder","Search");$(".company-investor-relations-news .form-type-textfield .controls").append(searchIconMarkup);$(".company-investor-relations-news .form-type-textfield .controls input").change(function(){$(".company-investor-relations-news .views-submit-button button").click();loadingSpinner($(".view-id-amat_news_block .view-content"),$(".view-id-amat_news_block"))});
$(".parts-search-icon").click(function(){$(".company-investor-relations-news .views-submit-button button").click()});Drupal.behaviors.updateIRNewsSearch={attach:function(context,settings){var searchIconMarkup='<a class="parts-search-icon" href="javascript:;">&nbsp;</a>';$(".company-investor-relations-news .form-type-textfield .controls input").attr("placeholder","Search");$(".company-investor-relations-news .form-type-textfield .controls").append(searchIconMarkup);$(".company-investor-relations-news .form-type-textfield .controls input").change(function(){$(".company-investor-relations-news .views-submit-button button").click();
loadingSpinner($(".view-id-amat_news_block .view-content"),$(".view-id-amat_news_block"))});$(".parts-search-icon").click(function(){$(".company-investor-relations-news .views-submit-button button").click()})}}}if(main_search){var searchIconMarkup='<a class="parts-search-icon" href="javascript:;">&nbsp;</a>';$(".page-search .form-type-textfield .controls input").attr("placeholder","Search");$(".page-search .form-type-textfield .controls").append(searchIconMarkup);$(".page-search .form-type-textfield .controls input").change(function(){$(".page-search .form-wrapper button").click()});
$(".parts-search-icon").click(function(){$(".page-search .form-wrapper button").click()})}if(request_info_form)$(".form-wrapper input").addClass("btn btn-primary");if(media_center){$("#media-center-menu a").click(function(){$("#media-center-menu ul li").removeClass("active");$(this).parent().addClass("active");$(".form-type-textfield input").val("");var term_id=$(this).attr("termid");$('#edit-field-media-category-tid option[value="'+term_id+'"]').attr("selected",true);loadingSpinner($(".view-id-amat2_media_browser .view-content"),
$(".view-id-amat2_media_browser"));$("#views-exposed-form-amat2-media-browser-image-list .form-submit").click();$("#views-exposed-form-amat2-media-browser-video-list .form-submit").click();$("#views-exposed-form-amat2-media-browser-document-tile-list .form-submit").click()});$("#media-center-search").change(function(){$('#edit-field-media-category-tid option[value="All"]').attr("selected",true);$(".form-type-textfield input").val($(this).val());loadingSpinner($(".view-id-amat2_media_browser .view-content"),
$(".view-id-amat2_media_browser"));$("#views-exposed-form-amat2-media-browser-image-list .form-submit").click();$("#views-exposed-form-amat2-media-browser-video-list .form-submit").click();$("#views-exposed-form-amat2-media-browser-document-tile-list .form-submit").click()})}if(product_library){$(".taxonomy-menu a.term").click(function(e){e.preventDefault;var parentCatText=$(this).parentsUntil("accordion-body").siblings(".accordion-heading").children("a").text().trim();var subCatText=$(this).text().trim();
$("#prod_scat_name").html(parentCatText+" | "+subCatText)});$(".accordion-heading a").click(function(){var headingText=$(this).text().trim();$("#prod_scat_name").html(headingText)});$(".alpha-index a").click(function(e){var index=$(this).attr("data-id");e.preventDefault();$("#edit-taxonomy-vocabulary-2-tid option").first().text("- Any -").attr("selected",true);$("#edit-field-alpha-index-value").val(index);loadingSpinner($(".view-display-id-product_library_tile_view_2 .view-content"),$(".view-display-id-product_library_tile_view_2"));
$("#edit-submit-amat2-product-selector").click();sendCustomTrackingEvent("event","Filter","Click","Alphabetical - "+index)});$("#accordion-products-menu .accordion-heading a").click(function(){if($.browser.msie&&parseInt($.browser.version,10)<=8)var headingText=$(this).text().trim();else var headingText=$(this).text().trim();if(headingText=="Alphabetical"){$("#edit-taxonomy-vocabulary-2-tid option").first().text("- Any -").attr("selected",true);$("#edit-field-alpha-index-value").val("");loadingSpinner($(".view-display-id-product_library_tile_view_2 .view-content"),
$(".view-display-id-product_library_tile_view_2"));$("#edit-submit-amat2-product-selector").click()}else if(headingText!=="Roll to Roll WEB Coating"){$("#edit-field-alpha-index-value").val("");var selectedText=$(this).text().trim();$("#edit-taxonomy-vocabulary-2-tid option").filter(function(){return $(this).text().trim()==selectedText}).attr("selected","selected");loadingSpinner($(".view-display-id-product_library_tile_view_2 .view-content"),$(".view-display-id-product_library_tile_view_2"));$("#edit-submit-amat2-product-selector").click();
sendCustomTrackingEvent("event","Filter","Click",selectedText)}});if(product_listing)$(".view-table-btn").addClass("active");else $(".view-tile-btn").addClass("active");$(".roll-to-roll").click(function(){$(".collapse.in").collapse("hide");$("#edit-keys").val("");$("#edit-title").val("");$("#product-library-search").val("");$("#edit-field-alpha-index-value").val("");$("#edit-taxonomy-vocabulary-2-tid option").val("2000").attr("selected",true);$("#edit-submit-amat2-product-selector").click();sendCustomTrackingEvent("event",
"Filter","Click","Roll to Roll WEB Coating");if(product_listing)loadingSpinner($(".view-display-id-product_library_list_view_2 .view-content"),$(".view-display-id-product_library_list_view_2"));else loadingSpinner($(".view-display-id-product_library_tile_view_2 .view-content"),$(".view-display-id-product_library_tile_view_2"))});$(".view-all-products-btn").click(function(){if(product_listing)loadingSpinner($(".view-display-id-product_library_list_view_2 .view-content"),$(".view-display-id-product_library_list_view_2"));
else loadingSpinner($(".view-display-id-product_library_tile_view_2 .view-content"),$(".view-display-id-product_library_tile_view_2"));$("#edit-keys").val("");$("#edit-title").val("");$("#product-library-search").val("");$("#edit-field-alpha-index-value").val("");$("#edit-taxonomy-vocabulary-2-tid option").first().text("- Any -").attr("selected",true);$("#edit-submit-amat2-product-selector").click()});$("#product-library-search").change(function(){if(product_listing)loadingSpinner($(".view-display-id-product_library_list_view_2 .view-content"),
$(".view-display-id-product_library_list_view_2"));else loadingSpinner($(".view-display-id-product_library_tile_view_2 .view-content"),$(".view-display-id-product_library_tile_view_2"));$("#edit-field-alpha-index-value").val("");$("#edit-taxonomy-vocabulary-2-tid option").first().text("- Any -").attr("selected",true);$("#edit-title").val($(this).val());$("#edit-submit-amat2-product-selector").click();$(".parts-search-icon").click(function(){$("#edit-submit-amat2-product-selector").click()})});$(".taxonomy_menu_wrapper h3").click(function(){if($.browser.msie&&
parseInt($.browser.version,10)<=8)var clickedText=$(this).text();else var clickedText=$(this).text().trim();if(clickedText=="Technical Glossary")console.log("redirecting to glossary page");else{$("#edit-keys").val("");$("#edit-title").val("");$("#product-library-search").val("");$("#edit-field-alpha-index-value").val("");if(product_listing)loadingSpinner($(".view-display-id-product_library_list_view_2 .view-content"),$(".view-display-id-product_library_list_view_2"));else loadingSpinner($(".view-display-id-product_library_tile_view_2 .view-content"),
$(".view-display-id-product_library_tile_view_2"));var menu_list_str="-"+$(this).text();var parent_list_str=$(this).parentsUntil("accordion-body").siblings(".accordion-heading").children().text().trim();var parent_list=0;$("#edit-taxonomy-vocabulary-2-tid option").each(function(){var select_list_str=$(this).text();if(select_list_str==parent_list_str)parent_list++;if(select_list_str==menu_list_str&&parent_list>0){console.log(parent_list);$(this).attr("selected",true);parent_list=0}$("#edit-submit-amat2-product-selector").click()})}});
$(".accordion-group").on("show hide",function(n){$(n.target).siblings(".accordion-heading").find(".accordion-toggle img").toggleClass("show hide")});$("ul.taxonomy-menu a.term").click(function(event){event.preventDefault();$("#edit-keys").val("");$("#edit-title").val("");$("#product-library-search").val("");$("#edit-field-alpha-index-value").val("");if(product_listing)loadingSpinner($(".view-display-id-product_library_list_view_2 .view-content"),$(".view-display-id-product_library_list_view_2"));
else loadingSpinner($(".view-display-id-product_library_tile_view_2 .view-content"),$(".view-display-id-product_library_tile_view_2"));var term=$(this).text();var menu_str="--"+term;var parent_str=$(this).parent().parent().siblings("h3").text();var parent_str_mod="-"+parent_str;var grand_parent_str=$(this).parentsUntil(".accordion-group").siblings(".accordion-heading").children().text().trim();var parent=0;var grand_parent=0;$("#edit-taxonomy-vocabulary-2-tid option").each(function(){var select_str=
$(this).text();if(select_str==grand_parent_str)grand_parent++;if(select_str==parent_str_mod)parent++;if(select_str==menu_str&&parent>0){if(grand_parent>0){$(this).attr("selected",true);grand_parent=0;return false}parent=0}});$("#edit-submit-amat2-product-selector").click();var event_str=grand_parent_str+" > "+parent_str+" > "+term;sendCustomTrackingEvent("event","Filter","Click",event_str)});if($(".term-2316 a.term").length)$(".term-2316 a.term").unbind("click")}if(req_quote){$("#edit-submitted-part-name").removeAttr("readonly");
$("#edit-submitted-rquote-part-id").removeAttr("readonly");$("#edit-submitted-rquote-category").removeAttr("readonly");$("#edit-submitted-sub-category").removeAttr("readonly")}if(products_page){var urlparams=getUrlParams();var searchIconMarkup='<a class="parts-search-icon" href="javascript:;">&nbsp;</a>';$(".products .form-type-textfield .controls input").attr("placeholder","Search");$(".products .form-type-textfield .controls").append(searchIconMarkup);if(urlparams.title)$(".edit-keys").val(urlparams.title);
$(".parts-search-icon").click(function(){$("#edit-submit-amat2-product-selector").click()})}if(any_parts){$(".views-table .views-field a").not(".rquote").click(function(){$(".views-table tbody").addClass("loading")});$(".pagination a").click(function(){$(".views-table").addClass("loading")});Drupal.behaviors.updateTableOpacity={attach:function(context,settings){$(".views-table .views-field a").not(".rquote").click(function(){$(".views-table tbody").addClass("loading")});$(".pagination a").click(function(){$(".views-table").addClass("loading")})}};
if(main_parts){var parts_firstCat=$("#accordion-parts-menu .accordion-heading #cat-1").text();var parts_firstSubCat=$("#accordion-parts-menu #scat-1 .accordion-inner").first().children().text();$(".view-amat-parts #edit-category").val(parts_firstCat);$(".view-amat-parts #edit-subcategory").val(parts_firstSubCat);$(".view-amat-parts #edit-submit-amat-parts").click();setTimeout(function(){$(".pane-amat-parts").show()},1500);$(".accordion-heading a").click(function(){var $this=$(this);var $accordion_body=
$this.parents(".accordion-group").find(".accordion-body");if(!$accordion_body.hasClass("in"))$accordion_body.find("div").first().click()});$(".accordion-body div").click(function(){$(".views-table").before($('<div class="parts-ajax-overlay"><div class="ajax-progress ajax-progress-throbber"><div class="throbber">&nbsp;</div></div></div>'));$(".views-table").addClass("loading");$("#parts-search").val("");$("#edit-partid, #edit-name, #edit-cip-number").val("");var li_val=$(this).attr("data");li_val=
li_val.split("@@");$("#edit-category").val(li_val[0]);$("#edit-subcategory").val(li_val[1]);$("#edit-category").trigger("change");$("#edit-subcategory").trigger("change");$("#scat_name").html(li_val[0]+" / "+li_val[1]);$("#edit-submit-amat-parts").click();$("#scat_name").fadeIn("slow")});$(".accordion-group").on("show hide",function(n){$(n.target).siblings(".accordion-heading").find(".accordion-toggle img").toggleClass("show hide")});var sPageURL=window.location.search.substring(1);if(sPageURL){var sURLVariables=
sPageURL.split("&");for(var i=0;i<sURLVariables.length;i++){var sParameterName=sURLVariables[i].split("=");if(sParameterName[0]=="name")$("#parts-search").val(sParameterName[1])}}$(document).on("click",".rquote",function(){var quotes=$(this).data("id");var quote_data=quotes.split("@@");$("#edit-submitted-part-name").val(quote_data[0]);$("#edit-submitted-rquote-part-id").val(quote_data[1]);$("#edit-submitted-rquote-category").val(quote_data[2]);$("#edit-submitted-sub-category").val(quote_data[3]);
$("#edit-submitted-rquote-name").attr("placeholder","Enter your name");$("#edit-submitted-rquote-email").attr("placeholder","Enter your email address");$(".webform-component-textfield input").click(function(){$(this).removeAttr("readonly")})})}if(prod_parts){var mainCat=$("#parts-menu .menu-item").attr("data");mainCat=mainCat.split("@@");$("#edit-category").val(mainCat[0]);$("#edit-submit-amat-parts").click();$(".menu-item a").click(function(){$(".views-table").before($('<div class="parts-ajax-overlay"><div class="ajax-progress ajax-progress-throbber"><div class="throbber">&nbsp;</div></div></div>'));
$(".views-table").addClass("loading");$("#parts-search").val("");$("#edit-partid").val("");$("#edit-name").val("");$("#edit-cip-number").val("");var subCat=$(this).parent().attr("data");subCat=subCat.split("@@");$("#edit-subcategory").val(subCat[1]);$("#edit-submit-amat-parts").click();$("#scat_name").html(subCat[1].toUpperCase());$("#scat_name").fadeIn("slow")});$(document).on("click",".rquote",function(){var quotes=$(this).data("id");var quote_data=quotes.split("@@");$("#edit-submitted-part-name").val(quote_data[0]);
$("#edit-submitted-rquote-part-id").val(quote_data[1]);$("#edit-submitted-rquote-category").val(quote_data[2]);$("#edit-submitted-sub-category").val(quote_data[3]);$("#edit-submitted-rquote-name").attr("placeholder","Enter your name");$("#edit-submitted-rquote-email").attr("placeholder","Enter your email address");$(".webform-component-textfield input").click(function(){$(this).removeAttr("readonly")})})}$("#parts-search").change(function(){$(this).addClass("search-processed");$(".views-table").before($('<div class="parts-ajax-overlay"><div class="ajax-progress ajax-progress-throbber"><div class="throbber">&nbsp;</div></div></div>'));
$(".views-table").addClass("loading");if(main_parts){$("#edit-category").val("");$("#edit-subcategory").val("")}if(prod_parts)$("#edit-subcategory").val("");$("#edit-partid, #edit-name, #edit-cip-number").val($(this).val());$("#edit-submit-amat-parts").click();$("#scat_name").fadeOut("slow")});$(".parts-search-icon").click(function(){$("#edit-submit-amat-parts").click()})}$("#node-3332209 .email, #node-3332210 .email, #node-3332423 .email").prop("placeholder","Enter email address");$("#edit-submitted-asset-use-4").change(function(){if(this.checked)$("#node-3332423 #edit-submitted-other").fadeIn("fast");
else $("#node-3332423 #edit-submitted-other").fadeOut("fast").val("")});if($.browser.msie&&parseInt($.browser.version,10)>8){var videoStyle=function(){$(".video video").wrap('<div class="video-controls-wrap"></div>');$(".video video").each(function(idx){var videoClass="video-play"+idx,videoPlay='<a class="'+videoClass+' video-play-button">Play</a>',$this=$(this),currentVid=$(this).get(0);currentVid.removeAttribute("controls");$("."+videoClass).live("click",function(){currentVid.play();currentVid.volume=
.5;$(this).fadeOut();currentVid.setAttribute("controls")});$this.after(videoPlay)})};videoStyle();$(".video video").live("click",function(){currentVid=$(this).get(0);currentVid.volume=.5})}if(!$.browser.msie&&!is_firefox&&!navigator.userAgent.match(/(iPod|iPhone|iPad)/)){var videoStyle=function(){$(".video video").wrap('<div class="video-controls-wrap"></div>');$(".video video").each(function(idx){var videoClass="video-play"+idx,videoPlay='<a class="'+videoClass+' video-play-button">Play</a>',$this=
$(this),currentVid=$(this).get(0);currentVid.removeAttribute("controls");$("."+videoClass).live("click",function(){currentVid.play();currentVid.volume=.5;$(this).fadeOut();currentVid.setAttribute("controls","true")});$this.after(videoPlay)})};videoStyle();$(".video video").live("click",function(){currentVid=$(this).get(0);currentVid.volume=.5})}$('#edit-field-portfolio-status-value option[value="All"]').text("Status");$('#edit-field-portfolio-location-value option[value="All"]').text("Location");
$('#edit-field-portfolio-sector-value option[value="All"]').text("Sector");$(".vertical-menu-list").closest(".panel-col-left").next(".panel-col-right").addClass("vertical-menu-list-right")});
Drupal.behaviors.updateExposedFilterAwards={attach:function(context){var findIt=$("#edit-field-award-category-value:not(.rewrite-processed)",context);if(findIt.length>0){findIt.addClass(".rewrite-processed");$("#edit-field-award-category-value option").each(function(){if($(this).attr("selected")){var selectedOption=$(this).val();$('#awards-landing-filter a[value="'+selectedOption+'"]').addClass("btn-current")}})}}};
Drupal.behaviors.updateSearchLabel={attach:function(context){$(".form-search.content-search .input-append",context).prepend('<label class="hide">Search</label>')}};function loadingSpinner(overlay,spinner){overlay.addClass("loading");spinner.append('<div class="ajax-progress ajax-progress-throbber"><div class="throbber">&nbsp;</div></div>')}
function rebuildTableForMobile(){var col_count=0;var markup="";markup+='<ul class="committee-chart-mobile">';$(".committee-chart thead th").each(function(){if($(this).text().length){markup+="<li>";markup+='<div class="com-accordion">'+$(this).text()+"</div>";markup+='<div class="member-group">';$(".committee-chart tbody tr").each(function(){var col_index=0;$(this).children("td").each(function(){if(col_index==col_count){var imageMarkup="";var extractedText=$(this).siblings("td").first().text();var extractedHref=
$(this).siblings("td").first().find("a").attr("href");if($(this).hasClass("com-icon-chair"))imageMarkup='<img src="/sites/all/themes/appliedmaterials_clean/images/committee-chair-icon.png" alt="Committee Chair">';if($(this).hasClass("com-icon-member"))imageMarkup='<img src="/sites/all/themes/appliedmaterials_clean/images/committee-icon.png" alt="Committee Member">';if($(this).hasClass("com-icon")){markup+='<div class="member-wrap">';markup+='<a href="'+extractedHref+'">'+extractedText+"</a>";markup+=
imageMarkup;markup+="</div>"}}col_index++})});markup+="</div>";markup+='<div class="committee-icon-group">';markup+='<span class="toggle-icons"></span>';markup+="</div></li>"}col_count++});markup+="</ul>";$(".pane-amat-utilities-committee-composition-block").html(markup);$(".committee-chart-mobile li").click(function(){$(this).find(".member-group").slideToggle();$(this).find(".committee-icon-group .toggle-icons").toggleClass("animate")})}
$(window).on("load",function(){var submitted=getParameterByName("sid");if(submitted)$(".signup-inside").html("<h3>Thank you for subscribing!</h3>");if($(".scroll-then-fixed-js").length){if(window.innerWidth>979)addFixedClassWhenScrolledTo($(".scroll-then-fixed-js"));else{console.log("mobile");addFixedClassWhenScrolledTo($(".scroll-then-fixed-mobile-js"))}$(".signup-inside input").blur(function(e){if($(this).val()){var inputText=$(this).val();$("#webform-client-form-3332207 .form-email").val(inputText)}})}});
function sendCustomTrackingEvent(hitType,eventCategory,eventAction,eventLabel){if(window.ga)ga("send",hitType,eventCategory,eventAction,eventLabel)}function getUrlParams(){var result={};var params=(window.location.search.split("?")[1]||"").split("&");for(var param in params)if(params.hasOwnProperty(param)){paramParts=params[param].split("=");result[paramParts[0]]=decodeURIComponent(paramParts[1]||"")}return result}
function enterToClick(input){input.keypress(function(e){if(e.which==13){$(this).siblings("button").click();return false}})}function addFixedClassWhenScrolledTo(element){var theLoc=element.offset().top;$(window).scroll(function(){if(theLoc>=$(window).scrollTop()){if(element.hasClass("fixed"))element.removeClass("fixed")}else if(!element.hasClass("fixed"))element.addClass("fixed")})}
function getParameterByName(name,url){if(!url)url=window.location.href;name=name.replace(/[\[\]]/g,"\\$&");var regex=new RegExp("[?&]"+name+"(=([^&#]*)|&|#|$)"),results=regex.exec(url);if(!results)return null;if(!results[2])return"";return decodeURIComponent(results[2].replace(/\+/g," "))}function onFullScreen(e){var isFullscreenNow=document.webkitFullscreenElement!==null;alert("Fullscreen "+isFullscreenNow)};;/**/
