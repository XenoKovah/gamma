import React from 'react';

import Table from '@material-ui/core/Table';
import TableBody from '@material-ui/core/TableBody';
import TableCell from '@material-ui/core/TableCell';
import TableHead from '@material-ui/core/TableHead';
import TableRow from '@material-ui/core/TableRow';
import Paper from '@material-ui/core/Paper';

import Typography from '@material-ui/core/Typography';

export default class ActionList extends React.Component {

    render() {
        let actions = [];
        for ( let key in this.props.actions) {
            actions.push(
                <TableRow>
                    <TableCell align="center">{key}</TableCell>
                    <TableCell align="center">{this.props.actions[key]}</TableCell>
                </TableRow>
            )
        }
        return (
            <Paper>
                <Typography color="inherit" variant="subtitle1" className="TableHeading">
                    <h3>Actions</h3>
                </Typography>
                <Table>
                    <TableHead>
                        <TableRow>
                            <TableCell align="center">{gettext('Actions')}</TableCell>
                            <TableCell align="center">{gettext('Points')}</TableCell>
                        </TableRow>
                    </TableHead>
                    <TableBody>
                            {actions}
                    </TableBody>
                </Table>
            </Paper>
        )
    }
}
