import { IMascotItems } from "../../interfaces/interfaces";
import clsx from "clsx";
import React from "react";
import { useMascotStore } from "../../state/mascot.state";
import DrawMascotItem from "../DrawMascotItem";

interface Props {
  items: IMascotItems[];
  selectedItem?: IMascotItems;
  dataKey: string;
}

const MascotItems = ({ items, selectedItem, dataKey }: Props) => {
  const {setSelectedMascotData, isLoading} = useMascotStore()

  interface Props {
    canvasRef: React.RefObject<HTMLCanvasElement>;
    items: IMascotItems[];
    selectedItem?: IMascotItems;
  }

  return (
    <>
      {
        !!items.length && items.map((item) => {
            return <>
              <li
                className={clsx("mascot-wardrobe-list-item", {
                  ['is-active']: selectedItem?.id === item.id,
                  ['is-disabled']: selectedItem?.id === -1 || isLoading,
                })}
                key={`${dataKey}Item_${item.id}`}
                onClick={()=>{
                  if (isLoading) {
                    return
                  }

                  setSelectedMascotData({
                    [dataKey]: item,
                  })
                }}
              >
                <div className="mascot-wardrobe-list-image-holder">
                  <div className="mascot-wardrobe-list-image">
                    <DrawMascotItem item={item} dataKey={dataKey} />
                  </div>
                </div>
                {item.name}
              </li>
            </>;
          }
        )
      }
    </>
  );
};

export default MascotItems;
