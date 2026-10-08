"use strict";

// Personal browser storage; never sends documents or notes to a remote service.
class PersonalStore {
  constructor() {
    this.connection = new Promise((resolve, reject) => {
      const request = indexedDB.open("atlas-personal", 1);
      request.onupgradeneeded = () => {
        for (const name of ["history", "saved"]) {
          if (!request.result.objectStoreNames.contains(name)) request.result.createObjectStore(name, { keyPath: "id" });
        }
      };
      request.onsuccess = () => {
        request.result.onversionchange = () => request.result.close();
        resolve(request.result);
      };
      request.onerror = () => reject(new Error("Personal storage is unavailable in this browser."));
      request.onblocked = () => reject(new Error("Close other Atlas tabs and try again to open personal storage."));
    });
    // Keep a failed initialization from becoming an unhandled rejection before use.
    this.connection.catch(() => {});
  }

  async operation(name, mode, callback) {
    const database = await this.connection;
    return new Promise((resolve, reject) => {
      const transaction = database.transaction(name, mode);
      const request = callback(transaction.objectStore(name));
      let value;
      request.onsuccess = () => { value = request.result; };
      transaction.oncomplete = () => resolve(value);
      transaction.onerror = transaction.onabort = () => reject(new Error("Could not save your changes. Browser storage may be full or unavailable. Your reading is still available."));
    });
  }

  get(name, id) { return this.operation(name, "readonly", store => store.get(id)); }
  count(name) { return this.operation(name, "readonly", store => store.count()); }
  list(name) { return this.operation(name, "readonly", store => store.getAll()).then(rows => rows.sort((a, b) => b.createdAt - a.createdAt)); }
  put(name, entry) { return this.operation(name, "readwrite", store => store.put(entry)); }
  delete(name, id) { return this.operation(name, "readwrite", store => store.delete(id)); }
  clear(name) { return this.operation(name, "readwrite", store => store.clear()); }

  async update(name, id, transform) {
    const database = await this.connection;
    return new Promise((resolve, reject) => {
      const transaction = database.transaction(name, "readwrite");
      const store = transaction.objectStore(name);
      const request = store.get(id);
      let result;
      request.onsuccess = () => {
        try {
          result = transform(request.result);
          if (result !== undefined) store.put(result);
        } catch { transaction.abort(); }
      };
      transaction.oncomplete = () => resolve(result);
      transaction.onerror = transaction.onabort = () => reject(new Error("Could not save your changes. Browser storage may be full or unavailable."));
    });
  }
}

const personalStore = new PersonalStore();
