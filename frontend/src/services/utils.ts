export function findLastIndex(array, searchKey, searchValue) {
    let index = array.slice().reverse().findIndex(x => x[searchKey] == searchValue);
    let count = array.length - 1
    let finalIndex = index >= 0 ? count - index : index;
    return finalIndex;
  }