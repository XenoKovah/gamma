import React from 'react';

import Filter from './Filter';


export default class FilterContainer extends React.Component {
    constructor(props) {
        super(props);

        this.onChangeFilter = this.onChangeFilter.bind(this);

    }

    onChangeFilter(key, value) {
        let filters = this.props.filters || {};

        switch(key) {
          case "start":
          case "end":
            let interval = filters.interval || {};
            if (value === null) {
              if (filters.interval) {
                delete filters.interval[key];
              }
              else {
                delete filters.interval;
              }
            } else {
              interval[key] = value;
            }

            if (Object.keys(interval).length !== 0) {
              filters.interval = interval;
            } else {
              delete filters.interval;
            }
            
            break;

          default:
            if ( value === null ) {
              delete filters[key]; 
            } else {
              filters[key] = value;
            }
        }
        this.props.filtersChanged(filters);
      }

    render() {
        return (
            <Filter {...this.props.filters} shouldFilterUpdate={this.props.shouldFilterUpdate} onChange={this.onChangeFilter}/>
        )
    }
}
