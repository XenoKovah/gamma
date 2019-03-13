import React from 'react';

import PropTypes from 'prop-types';

import Input from '@material-ui/core/Input';
import InputLabel from '@material-ui/core/InputLabel';
import FormControl from '@material-ui/core/FormControl';


export default class FilterContainer extends React.Component {
    constructor(props) {
        super(props);
    }

    render() {
        return (
            <FormControl>
                <InputLabel htmlFor="count-input">Count </InputLabel>
                <Input id="count-input" inputProps={{type: "text"}}
                />

            </FormControl>
        )
    }
}

FilterContainer.propTypes = {
    filters: PropTypes.object
}