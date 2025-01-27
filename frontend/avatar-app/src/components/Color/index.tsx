import styled from 'styled-components';

const MascotColor = styled.div`
  background-color: ${props => props.color};
  //width: 44px;  // Якщо всім кольорам потрібна однакова ширина
`;

export default MascotColor;
