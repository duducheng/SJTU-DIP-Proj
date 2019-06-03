const app = new Vue({
    el: '#app',
    data: {
        pid: 1,
        img: "",
        files: [],
        choices: [],
        choice: "",
        inputVisible: false,
        optionValue: ""
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
            this.$http.post('http://localhost:5005/state', { 'img': this.img }).then(
                this.updateState,
                console.log
            );
        }
    },
    methods: {
        project: function(pid) {
            this.pid = pid;
            this.$http.post('http://localhost:5005/state', { 'pid': this.pid }).then(
                this.updateState,
                console.log
            );
        },
        getChoice: function(choice) {
            this.choice = choice;
            this.$http.post('http://localhost:5005/state', { 'choice': this.choice }).then(
                this.updateState,
                console.log
            );
        },
        updateState: function(response) {
            this.files = response.body.files;
            this.choices = response.body.choices;
            this.choice = response.body.choice;
            this.inputVisible = response.body.inputVisible;
            this.pid = response.body.pid;
            this.img = response.body.img;
            this.optionValue = response.body.optionValue;
        },
        updateValue: function() {
            console.log(this.optionValue);
            this.$http.post('http://localhost:5005/state', { 'optionValue': this.optionValue }).then(
                this.updateState,
                console.log
            );
        }
    }
});