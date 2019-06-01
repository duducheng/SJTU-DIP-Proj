const app = new Vue({
    el: '#app',
    data: {
        pid: 1,
        img: "",
        files: []
    },
    created: function() {
        console.log("READY");
        console.log(this.pid);
        this.$http.get('http://localhost:5005/state').then(
            this.updateState,
            console.log
        );
    },
    watch: {
        img: function(value) {
            console.log(value);
            this.$http.post('http://localhost:5005/state', { 'img': this.img }).then(console.log);
        }
    },
    methods: {
        project: function(pid) {
            this.pid = pid;
            this.$http.post('http://localhost:5005/state', { 'pid': this.pid }).then(console.log);
        },
        updateState: function(response) {
            this.files = response.body.files;
            this.pid = response.body.pid;
            this.img = response.body.img;
        }
    }
});