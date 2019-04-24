// Functions

function validateEmail(email) {
    var re = /^[a-z0-9\.\-\_]+@[a-z0-9\-\_]+(\.[a-z0-9\-\_]+){1,4}$/;
    return re.test(email.toLowerCase());
}

// Vue component and filter

if (typeof (Vue !== 'undefined')) {

    Vue.filter('datetime_filter', function (value) {
        delta = new Date().getTime()/1000- value;
        if (delta < 60) {
            return Math.round(delta) + ' seconds ago';
        }
        if (delta < 3600) {
            return Math.round(delta / 60) + ' minutes ago';
        }
        if (delta < 86400) {
            return Math.round(delta / 3600) + ' hous ago';
        }
        if (delta < 604800) {
            return Math.round(delta / 86400) + ' days ago';
        }
        dt = new Date(value * 1000);
        return dt.getFullYear() + '-' + (dt.getMonth() + 1) + '-' + dt.getDate();
    });

    Vue.component('blog', {
        props: ['info', 'images'],
        template: `
                <div class="blogs">
                    <h3 class="title"><a :href="'/blog/'+info.id">{{ info.name }}</a></h3>
                    <div class="meta">
                        <i class="icon fa-user"></i> {{ info.user_name }} &nbsp;
                        <i class="icon fa-calendar"></i> {{ info.created_at | datetime_filter }} &nbsp;
                        <i class="icon fa-eye"></i> {{ info.readers }} &nbsp;
                    </div>
                    <div class="clear"></div>
                    <a :href="'/blog/'+info.id"><img :src="'..' + images.blog_path + 'imgS_' + info.id + '.jpg'" alt="图片被吞掉了！"/></a>
                    <p class="summary" style="padding: 0.25rem 0 0 0;">{{ info.summary }}</p>
                    <div class="clear"></div>
                </div>
                `
    });

    Vue.component('pagination', {
        props: ['page_index', 'has_previous', 'has_next', 'page_count', 'range'],
        template: '<ul class="uk-pagination">' +
                '<li v-if="! has_previous" class="unused"><a><i class="icon fa-angle-double-left"></i></a></li>' +
                '<li v-if="has_previous"><a v-on:click=\'$emit("changeinfos", page_index-1)\' href="#0"><i class="icon fa-angle-double-left"></i></a></li>' +
                '<template v-for="item in range">' +
                '<li v-if="item!==page_index"><a v-on:click=\'$emit("changeinfos", item)\' href="#0">{{ item }}</a></li>' +
                '<li v-else class="used"><a>{{ page_index }}</a></li>' +
                '</template>' +
                '<li v-if="! has_next" class="unused"><a><i class="icon fa-angle-double-right"></i></a></li>' +
                '<li v-if="has_next"><a v-on:click=\'$emit("changeinfos", page_index+1)\' href="#0"><i class="icon fa-angle-double-right"></i></a></li>' +
                '</ul>'
    });

    Vue.component('incomment', {
        props: ['reply', 'images'],
		data() {
			return {
				user_img: '/static/images/user.jpg'
			}
		},
		mounted: function () {
			this.user_img = this.images.user_path + this.reply.user_id + '.jpg';
		},
        template: `
                <div class="in_comment">
                    <img class="in_user_img" :src="this.user_img" @error="user_img='/static/images/user.jpg'" />
                    <div class="user_info">
                        {{reply.user_name}}
                    </div>
                    <div class="in_user_art">
                        {{reply.content}}
                    </div>
                    <div class="in_user_sel">
                        <span>{{reply.created_at | datetime_filter}}</span>
                    </div>
                </div>
                `
    });
    
    Vue.component('outcomment', {
        props: ['comment', 'images', 'id_img', 'isUser'],
        data() {
            return {
                content: '',
                name: '',
                in_visible: {display: 'none'},
				user_img: '/static/images/user.jpg',
            }
        },
        methods: {
            show_form: function (event) {
                if (this.isUser)
                    this.in_visible = { display: 'block' };
                else
                    alert("请先登录或注册！");
            },
            submit: function (event) {
                if (this.content === '') {
                    alert("评论不能为空！");
                    return;
                }
                if (this.name === '') {
                    this.name = this.comment.user_name
                }
                axios.post('/api/reply/new/' + this.comment.id, {
                    content: this.content,
                    target_name: this.name
                })
                    .then(location.reload())
                    .catch(err => console.log(err));
            }
        },
		mounted: function() {
			this.user_img = this.images.user_path + this.comment.user_id + '.jpg';
		},
        template: `
                <div class="out_comment">
                    <img class="user_img" :src="this.user_img" @error.once="user_img='/static/images/user.jpg'" />
                    <div class="user_info">
                        {{comment.user_name}}
                    </div>
                    <div class="user_art">
                        {{comment.content}}
                    </div>
                    <div class="user_sel">
                        <span>{{comment.created_at | datetime_filter}}</span>
                        <span><a @click="show_form" href="#0">回复</a></span>
                    </div>
                    <incomment v-for="reply in comment.replies"
                                v-bind:key="reply.id"
                                v-bind:reply="reply"
                                v-bind:images="images"
                                ></incomment>
                    <form class="user_form" v-bind:style="in_visible" @submit.prevent="submit">
                        <img class="user_img" :src="id_img" />
                        <textarea v-model="content"></textarea>
                        <input type="submit" value="回复" />
                    </form>
                </div>
                `
    });

}