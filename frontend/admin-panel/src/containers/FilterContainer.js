import React from 'react';

import PropTypes from 'prop-types';

import Input from '@material-ui/core/Input';
import InputLabel from '@material-ui/core/InputLabel';
import FormControl from '@material-ui/core/FormControl';

import Filter from './Filter'


export default class FilterContainer extends React.Component {
    constructor(props) {
        super(props);

        this.onChangeFilter = this.onChangeFilter.bind(this);

    }

    onChangeFilter(key, value) {
        let filters = this.props.filters || {interval: {}};
        switch(key) {
          case 'start':
            filters.interval[key] = value;
            break;
          case 'end':
            filters.interval[key] = value;
            break;
          default:
            filters[key] = value;
        }
        this.props.filtersChanged(filters);
      }

    render() {
        return (
            <Filter {...this.props.filters} onChange={this.onChangeFilter}/>
        )
    }
};

// FilterContainer.propTypes = {
//     filters: PropTypes.array
// }