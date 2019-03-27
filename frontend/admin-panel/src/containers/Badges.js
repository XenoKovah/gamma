import React from 'react';

import Badge from '../components/Badge';


export default class Badges extends React.Component {
    constructor(props) {
        super(props);

        this.state = {
            badges: []
        }

    }

    getBadges() {
        fetch('/api/v0/statuses/')
        .then(result => result.json())
        .then((result)=>{
            console.log(result);
            this.setState({
                badges: result
            })
        })
    }

    componentDidMount() {
        this.getBadges();
    }

    render() {
        return (
            this.state.badges.map((badge, ind) => {
                return <Badge {...badge} key={ind}/>
            })
        )
    }
}
