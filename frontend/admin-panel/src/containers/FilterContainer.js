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
        this.removeFilter = this.removeFilter.bind(this);

        // this.state = {
        //     filters: props.filters
        // }

    }

    onChangeFilter(id, key, value) {
        let filters = this.props.filters;
        let filter = filters[this.props.getIndex(filters, id)];
        console.log('onChangeFilter', id, key, value, filter);
        switch(key) {
          case 'start':
            filter.interval[key] = value;
            break;
          case 'end':
            filter.interval[key] = value;
            break;
          default:
            filter[key] = value;
        }
        this.props.filtersChanged(filters)
      }

    removeFilter(id) {
        let filters = this.props.filters;
        filters.splice(this.props.getIndex(filters, id), 1);
        this.props.filtersChanged(filters)
    }

    render() {
        return (
            this.props.filters.map((filter, ind) => {
                return (
                    <div className="FilterItem">
                        <Filter key={filter.id} id={filter.id} {...filter} removeFilter={this.removeFilter} onChange={this.onChangeFilter}/>
                    </div>
                )
            })
        )
    }
};

FilterContainer.propTypes = {
    filters: PropTypes.array
}